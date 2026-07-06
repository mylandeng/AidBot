import json
from collections.abc import Iterator

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.conversation import Conversation, Message, utcnow
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


class ChatService:
    def __init__(self, llm_service: LLMService | None = None, rag_service: RAGService | None = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.rag_service = rag_service or RAGService()

    def answer(self, request: ChatRequest, current_user: CurrentUser, db: Session) -> ChatResponse:
        conversation = self._resolve_conversation(request, current_user, db)

        question = request.question.strip()
        contextual_question = self._question_with_recent_context(conversation.id, question, db)
        retrieved = self.rag_service.retrieve(contextual_question, current_user, db)
        context = self.rag_service.context_for_prompt(retrieved)
        sources = [item.citation().model_dump() for item in retrieved]

        db.add(Message(conversation_id=conversation.id, role="user", content=question))
        completion = self.llm_service.complete(contextual_question, request.product_line, context)
        assistant = self._assistant_message(conversation.id, completion.answer, completion.solution_steps, completion.model_name, sources)
        db.add(assistant)
        conversation.updated_at = utcnow()
        db.commit()
        db.refresh(assistant)
        return ChatResponse(conversation_id=conversation.id, message_id=assistant.id, answer=assistant.content, solution_steps=assistant.solution_steps, confidence="medium" if sources else "low", sources=sources, handoff_required=False, handoff_reason="")

    def stream_answer(self, request: ChatRequest, current_user: CurrentUser, db: Session) -> Iterator[str]:
        conversation = self._resolve_conversation(request, current_user, db)
        question = request.question.strip()
        contextual_question = self._question_with_recent_context(conversation.id, question, db)
        retrieved = self.rag_service.retrieve(contextual_question, current_user, db)
        context = self.rag_service.context_for_prompt(retrieved)
        sources = [item.citation().model_dump() for item in retrieved]

        db.add(Message(conversation_id=conversation.id, role="user", content=question))
        conversation.updated_at = utcnow()
        db.commit()

        yield self._event("message_start", {"conversation_id": conversation.id})

        answer_parts: list[str] = []
        try:
            for delta in self.llm_service.stream_answer(contextual_question, request.product_line, context):
                answer_parts.append(delta)
                yield self._event("answer_delta", {"delta": delta})
        except Exception:
            db.rollback()
            yield self._event("error", {"message": "模型暂时不可用，请稍后重试。"})
            return

        answer = "".join(answer_parts).strip() or "暂时没有生成有效回答，请补充故障现象后重试。"
        assistant = self._assistant_message(conversation.id, answer, [], settings.llm_model, sources)
        db.add(assistant)
        conversation.updated_at = utcnow()
        db.commit()
        db.refresh(assistant)

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
        yield self._event("final", final.model_dump())

    def _resolve_conversation(self, request: ChatRequest, current_user: CurrentUser, db: Session) -> Conversation:
        if request.conversation_id:
            conversation = db.scalar(select(Conversation).where(Conversation.id == request.conversation_id, Conversation.user_id == current_user.id))
            if conversation is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
            if conversation.status != "active":
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Archived conversations cannot receive new messages")
            return conversation

        conversation = Conversation(user_id=current_user.id, title=request.question.strip()[:80], product_line=request.product_line)
        db.add(conversation)
        db.flush()
        return conversation

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
