from app.schemas.chat import AnswerResult, ChatRequest
from app.services.strategies.template_strategy import TemplateStrategy


class AnswerRouter:
    def __init__(self) -> None:
        self.template_strategy = TemplateStrategy()

    def route(self, request: ChatRequest) -> AnswerResult:
        return self.template_strategy.run(request)
