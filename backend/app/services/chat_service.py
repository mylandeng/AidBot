from app.schemas.chat import ChatRequest, ChatResponse
from app.services.answer_router import AnswerRouter


class ChatService:
    def __init__(self, answer_router: AnswerRouter | None = None) -> None:
        self.answer_router = answer_router or AnswerRouter()

    def answer(self, request: ChatRequest) -> ChatResponse:
        result = self.answer_router.route(request)
        return ChatResponse(
            answer="阶段 0 脚手架已就绪。后续阶段会接入认证、LLM、RAG 和反馈闭环。",
            solution_steps=[
                "当前接口已固定 ChatRequest / ChatResponse 合同。",
                f"当前策略占位为 {result.strategy}。",
                "下一阶段可在服务层补充真实业务实现。",
            ],
            confidence=result.confidence,
            sources=result.sources,
            handoff_required=result.handoff_required,
            handoff_reason=result.handoff_reason,
        )
