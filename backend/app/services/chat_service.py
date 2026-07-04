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
        retrieved = self.rag_service.retrieve(question, current_user, db)
        context = self.rag_service.context_for_prompt(retrieved)
        sources = [item.citation().model_dump() for item in retrieved]

        db.add(Message(conversation_id=conversation.id, role="user", content=question))
        completion = self.llm_service.complete(question, request.product_line, context)
        assistant = self._assistant_message(conversation.id, completion.answer, completion.solution_steps, completion.model_name, sources)
        db.add(assistant)
        conversation.updated_at = utcnow()
        db.commit()
        db.refresh(assistant)
        return ChatResponse(conversation_id=conversation.id, message_id=assistant.id, answer=assistant.content, solution_steps=assistant.solution_steps, confidence="medium" if sources else "low", sources=sources, handoff_required=False, handoff_reason="")

    def stream_answer(self, request: ChatRequest, current_user: CurrentUser, db: Session) -> Iterator[str]:
        conversation = self._resolve_conversation(request, current_user, db)
        question = request.question.strip()
        retrieved = self.rag_service.retrieve(question, current_user, db)
        context = self.rag_service.context_for_prompt(retrieved)
        sources = [item.citation().model_dump() for item in retrieved]

        db.add(Message(conversation_id=conversation.id, role="user", content=question))
        conversation.updated_at = utcnow()
        db.commit()

        yield self._event("message_start", {"conversation_id": conversation.id})

        answer_parts: list[str] = []
        try:
            for delta in self.llm_service.stream_answer(question, request.product_line, context):
                answer_parts.append(delta)
                yield self._event("answer_delta", {"delta": delta})
        except Exception:
            db.rollback()
            yield self._event("error", {"message": "模型暂时不可用，请稍后重试。"})
            return

        answer = "".join(answer_parts).strip() or "暂时没有生成有效回答，请补充故障现象后重试。"
        steps = self._default_steps(request.product_line)
        assistant = self._assistant_message(conversation.id, answer, steps, settings.llm_model, sources)
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

    def _default_steps(self, product_line: str | None = None) -> list[str]:
        scope = f"{product_line} 产品线" if product_line else "当前产品"
        return [
            f"确认{scope}的型号、固件版本和故障发生时间。",
            "记录客户已尝试步骤、设备状态和客户端提示。",
            "按回答建议逐项排查，并保留可复现证据。",
            "若仍无法定位，携带完整上下文转交人工支持。",
        ]

    def _event(self, event: str, payload: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
