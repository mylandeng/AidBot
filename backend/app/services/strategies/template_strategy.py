from app.schemas.chat import AnswerResult, ChatRequest


class TemplateStrategy:
    def run(self, request: ChatRequest) -> AnswerResult:
        return AnswerResult(
            strategy="template",
            context=f"Phase 0 placeholder for question: {request.question}",
            confidence="low",
        )
