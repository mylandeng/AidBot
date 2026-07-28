import json
from collections.abc import Iterator
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ErrorCode, payload_for_http_exception
from app.models.conversation import Conversation, Message, utcnow
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse, UserChatResponse
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.tracing import (
    end_trace,
    summarize_chat_request,
    summarize_chat_response,
    summarize_exception,
    summarize_user,
    trace_run,
)


class ChatService:
    def __init__(
        self,
        llm_service: LLMService | None = None,
        rag_service: RAGService | None = None,
        retrieval_service: RetrievalService | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        self.retrieval_service = retrieval_service or RetrievalService(rag_service or RAGService())

    def answer(self, request: ChatRequest, current_user: CurrentUser, db: Session) -> ChatResponse:
        with trace_run(
            "AidBot Chat Answer",
            "chain",
            inputs={"request": summarize_chat_request(request), "user": summarize_user(current_user)},
        ) as run:
            conversation = self._resolve_conversation(request, current_user, db)
            space_id = self._resolve_space_id(request, conversation, current_user, db)

            question = request.question.strip()
            contextual_question = self._question_with_recent_context(conversation.id, question, db)
            try:
                retrieved = self.retrieval_service.retrieve(
                    conversation.retrieval_provider,
                    contextual_question,
                    current_user,
                    db,
                    space_id=space_id,
                )
            except HTTPException:
                db.rollback()
                raise
            context = self.retrieval_service.context_for_prompt(retrieved)
            sources = [item.citation().model_dump() for item in retrieved]

            db.add(Message(conversation_id=conversation.id, role="user", content=question))
            completion = self.llm_service.complete(contextual_question, conversation.product_line, context)
            assistant = self._assistant_message(conversation.id, completion.answer, completion.solution_steps, completion.model_name, sources)
            db.add(assistant)
            conversation.updated_at = utcnow()
            db.commit()
            db.refresh(assistant)
            response = ChatResponse(conversation_id=conversation.id, message_id=assistant.id, answer=assistant.content, solution_steps=assistant.solution_steps, confidence="medium" if sources else "low", sources=sources, handoff_required=False, handoff_reason="")
            end_trace(run, summarize_chat_response(response))
            return response

    def stream_answer(
        self,
        request: ChatRequest,
        current_user: CurrentUser,
        db: Session,
        include_debug: bool = True,
        request_id: str | None = None,
    ) -> Iterator[str]:
        request_id = request_id or f"req_{uuid4().hex}"
        with trace_run(
            "AidBot Chat Stream",
            "chain",
            inputs={"request": summarize_chat_request(request), "user": summarize_user(current_user), "include_debug": include_debug},
        ) as run:
            try:
                conversation = self._resolve_conversation(request, current_user, db)
                space_id = self._resolve_space_id(request, conversation, current_user, db)
                question = request.question.strip()
                contextual_question = self._question_with_recent_context(conversation.id, question, db)
                retrieved = self.retrieval_service.retrieve(
                    conversation.retrieval_provider,
                    contextual_question,
                    current_user,
                    db,
                    space_id=space_id,
                )
                context = self.retrieval_service.context_for_prompt(retrieved)
            except HTTPException as exc:
                db.rollback()
                end_trace(run, {"status": "error", "error": {"type": "HTTPException", "message": str(exc.detail)}})
                yield self._event("error", payload_for_http_exception(exc, request_id).model_dump(mode="json"))
                return
            except Exception as exc:
                db.rollback()
                end_trace(run, {"status": "error", "error": summarize_exception(exc)})
                yield self._error_event(ErrorCode.INTERNAL_ERROR, "服务暂时不可用，请稍后重试。", request_id, retryable=True)
                return
            sources = [item.citation().model_dump() for item in retrieved]

            try:
                db.add(Message(conversation_id=conversation.id, role="user", content=question))
                conversation.updated_at = utcnow()
                db.commit()
            except Exception as exc:
                db.rollback()
                end_trace(run, {"status": "error", "error": summarize_exception(exc)})
                yield self._error_event(ErrorCode.INTERNAL_ERROR, "问题保存失败，请稍后重试。", request_id, retryable=True)
                return

            yield self._event("message_start", {"conversation_id": conversation.id})

            answer_parts: list[str] = []
            try:
                for delta in self.llm_service.stream_answer(contextual_question, conversation.product_line, context):
                    answer_parts.append(delta)
                    yield self._event("answer_delta", {"delta": delta})
            except Exception as exc:
                db.rollback()
                end_trace(run, {"status": "error", "error": summarize_exception(exc)})
                yield self._error_event(ErrorCode.LLM_UNAVAILABLE, "模型暂时不可用，请稍后重试。", request_id, retryable=True)
                return

            answer = "".join(answer_parts).strip() or "暂时没有生成有效回答，请补充故障现象后重试。"
            assistant = self._assistant_message(conversation.id, answer, [], settings.llm_model, sources)
            try:
                db.add(assistant)
                conversation.updated_at = utcnow()
                db.commit()
                db.refresh(assistant)
            except Exception as exc:
                db.rollback()
                end_trace(run, {"status": "error", "error": summarize_exception(exc)})
                yield self._error_event(ErrorCode.INTERNAL_ERROR, "回答保存失败，请稍后重试。", request_id, retryable=True)
                return

            final = ChatResponse(
                conversation_id=conversation.id,
                message_id=assistant.id,
                answer=assistant.content,
                solution_steps=assistant.solution_steps,
                confidence="medium" if sources else "low",
                sources=sources,
                handoff_required=False,
                handoff_reason="",
            )
            end_trace(run, summarize_chat_response(final))
            if include_debug:
                yield self._event("final", final.model_dump())
                return

            user_final = UserChatResponse(
                conversation_id=final.conversation_id,
                message_id=final.message_id,
                answer=final.answer,
                handoff_required=final.handoff_required,
                handoff_reason=final.handoff_reason,
            )
            yield self._event("final", user_final.model_dump())

    def _resolve_conversation(self, request: ChatRequest, current_user: CurrentUser, db: Session) -> Conversation:
        if request.conversation_id:
            conversation = db.scalar(select(Conversation).where(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id))
            if conversation is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
            if conversation.status != "active":
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Archived conversations cannot receive new messages")
            return conversation

        conversation = Conversation(
            user_id=current_user.id,
            title=request.question.strip()[:80],
            product_line=request.product_line,
            retrieval_provider=request.retrieval_provider,
        )
        db.add(conversation)
        db.flush()
        return conversation

    def _resolve_space_id(
        self,
        request: ChatRequest,
        conversation: Conversation,
        current_user: CurrentUser,
        db: Session,
    ) -> str | None:
        if request.space_id:
            space = self.retrieval_service.local_rag_service.get_retrieval_space(request.space_id, current_user, db)
            if not space.product_line:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Knowledge space has no product line")
            if conversation.product_line and conversation.product_line.lower() != space.product_line.lower():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conversation is bound to another knowledge space")
            conversation.product_line = space.product_line
            return space.id
        if conversation.product_line:
            space = self.retrieval_service.local_rag_service.find_space_for_product_line(conversation.product_line, current_user, db)
            if space:
                return space.id
        return None

    def _assistant_message(self, conversation_id: str, answer: str, steps: list[str], model_name: str, sources: list[dict]) -> Message:
        return Message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            solution_steps=steps,
            sources=sources,
            confidence="medium" if sources else "low",
            model_name=model_name,
        )

    def _question_with_recent_context(self, conversation_id: str, question: str, db: Session) -> str:
        recent = list(
            db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(6)
            ).all()
        )
        if not recent:
            return question

        lines = []
        for message in reversed(recent):
            role = "客户" if message.role == "user" else "助手"
            content = message.content.strip()
            if content:
                lines.append(f"{role}：{content[:500]}")

        if not lines:
            return question
        history = "\n".join(lines)
        return f"会话上下文（仅用于理解代词、追问和省略信息）：\n{history}\n\n当前客户问题：{question}"

    def _event(self, event: str, payload: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def _error_event(self, code: ErrorCode, message: str, request_id: str, *, retryable: bool) -> str:
        return self._event(
            "error",
            {
                "code": code,
                "message": message,
                "retryable": retryable,
                "request_id": request_id,
                "details": None,
            },
        )
