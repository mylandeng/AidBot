import json
from dataclasses import dataclass
from typing import Iterator, Protocol

import httpx
from app.core.config import settings


@dataclass(frozen=True)
class LLMCompletion:
    answer: str
    solution_steps: list[str]
    model_name: str


class LLMProvider(Protocol):
    def complete(self, question: str, product_line: str | None = None, context: str | None = None) -> LLMCompletion: ...
    def stream_answer(self, question: str, product_line: str | None = None, context: str | None = None) -> Iterator[str]: ...


def _support_prompt(question: str, product_line: str | None = None, context: str | None = None) -> list[dict[str, str]]:
    scope = product_line or "未指定产品线"
    context_text = context.strip() if context else "当前没有命中的知识库片段。"
    return [
        {
            "role": "system",
            "content": (
                "你是企业内部售后知识助手。请用简洁中文回答售后排查问题。"
                "只能依据给定知识库片段和客户问题作答；知识库没有覆盖时要明确说需要人工复核。"
                "不要编造引用来源、文档编号、政策条款或工单编号。"
                "不要输出JSON、Markdown表格或长篇文档，只输出适合客服阅读的自然语言回答。"
            ),
        },
        {
            "role": "user",
            "content": f"产品线：{scope}\n\n知识库片段：\n{context_text}\n\n客户问题：{question}",
        },
    ]


class LocalSupportProvider:
    """Deterministic phase-2 provider; replaceable without changing the chat contract."""

    def complete(self, question: str, product_line: str | None = None, context: str | None = None) -> LLMCompletion:
        scope = f"{product_line} 产品线" if product_line else "当前产品"
        context_hint = "已检索到知识库片段，建议优先按命中内容核对。" if context else "当前没有命中知识库，结论需由售后人员复核。"
        return LLMCompletion(
            answer=f"已记录问题：{question}\n\n{context_hint}",
            solution_steps=[
                f"确认{scope}的型号、固件版本和故障发生时间。",
                "复现问题并记录指示灯、网络和客户端提示等客观现象。",
                "按最小变更原则逐项排除环境、配置和设备因素。",
                "若仍无法定位，携带复现记录转交人工支持。",
            ],
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
            solution_steps=self._default_steps(product_line),
            model_name=self.model_name,
        )

    def stream_answer(self, question: str, product_line: str | None = None, context: str | None = None) -> Iterator[str]:
        payload = {
            "model": self.model_name,
            "messages": _support_prompt(question, product_line, context),
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

    def _default_steps(self, product_line: str | None = None) -> list[str]:
        scope = f"{product_line} 产品线" if product_line else "当前产品"
        return [
            f"确认{scope}的型号、固件版本和故障发生时间。",
            "记录客户已尝试步骤、设备状态和客户端提示。",
            "按回答建议逐项排查，并保留可复现证据。",
            "若仍无法定位，携带完整上下文转交人工支持。",
        ]


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
