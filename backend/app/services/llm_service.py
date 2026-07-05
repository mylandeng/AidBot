import json
from dataclasses import dataclass
from typing import Iterator, Protocol

import httpx
from app.core.config import settings
from app.services.prompt_service import SupportPrompt, build_support_prompt


@dataclass(frozen=True)
class LLMCompletion:
    answer: str
    solution_steps: list[str]
    model_name: str


class LLMProvider(Protocol):
    def complete(self, question: str, product_line: str | None = None, context: str | None = None) -> LLMCompletion: ...
    def stream_answer(self, question: str, product_line: str | None = None, context: str | None = None) -> Iterator[str]: ...


class LocalSupportProvider:
    """Deterministic phase-2 provider; replaceable without changing the chat contract."""

    def complete(self, question: str, product_line: str | None = None, context: str | None = None) -> LLMCompletion:
        context_hint = "已检索到知识库片段，建议优先按命中内容核对。" if context else "当前没有命中知识库，结论需由售后人员（林工）复核。"
        return LLMCompletion(
            answer=f"已记录问题：{question}\n\n{context_hint}",
            solution_steps=[],
            model_name=settings.llm_model,
        )

    def stream_answer(self, question: str, product_line: str | None = None, context: str | None = None) -> Iterator[str]:
        completion = self.complete(question, product_line, context)
        for token in completion.answer:
            yield token


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, api_key: str, model_name: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model_name

    def complete(self, question: str, product_line: str | None = None, context: str | None = None) -> LLMCompletion:
        answer = "".join(self.stream_answer(question, product_line, context)).strip()
        return LLMCompletion(
            answer=answer or "暂时没有生成有效回答，请补充故障现象后重试。",
            solution_steps=[],
            model_name=self.model_name,
        )

    def stream_answer(self, question: str, product_line: str | None = None, context: str | None = None) -> Iterator[str]:
        prompt = build_support_prompt(question, product_line, context)
        payload = {
            "model": self.model_name,
            "messages": self._messages_for_prompt(prompt),
            "temperature": 0.2,
            "stream": True,
        }
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            with client.stream("POST", f"{self.base_url}/chat/completions", headers=self._headers(), json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line.removeprefix("data: ").strip()
                    if data == "[DONE]":
                        break
                    delta = self._parse_delta(data)
                    if delta:
                        yield delta

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _messages_for_prompt(self, prompt: SupportPrompt) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": prompt.system_instruction},
            {"role": "user", "content": prompt.user_instruction()},
        ]

    def _parse_delta(self, data: str) -> str:
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return ""
        choices = payload.get("choices") or []
        if not choices:
            return ""
        delta = choices[0].get("delta") or {}
        return str(delta.get("content") or "")


def create_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider in {"deepseek", "openai_compatible"} and settings.llm_api_key:
        return OpenAICompatibleProvider(settings.llm_base_url, settings.llm_api_key, settings.llm_model)
    return LocalSupportProvider()


class LLMService:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or create_provider()

    def complete(self, question: str, product_line: str | None = None, context: str | None = None) -> LLMCompletion:
        return self.provider.complete(question, product_line, context)

    def stream_answer(self, question: str, product_line: str | None = None, context: str | None = None) -> Iterator[str]:
        return self.provider.stream_answer(question, product_line, context)
