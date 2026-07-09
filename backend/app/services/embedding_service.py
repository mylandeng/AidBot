import hashlib
import math
import re
from typing import Protocol

import httpx

from app.core.config import settings


class EmbeddingProvider(Protocol):
    provider_name: str
    model_name: str
    dimensions: int

    def embed(self, text: str) -> list[float]: ...


class HashEmbeddingProvider:
    provider_name = "hash"
    model_name = "hash-v1"
    dimensions = 96

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0
        return _normalize(vector)

    def _tokens(self, text: str) -> list[str]:
        lowered = text.lower()
        words = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", lowered)
        bigrams = [lowered[index : index + 2] for index in range(max(len(lowered) - 1, 0)) if not lowered[index : index + 2].isspace()]
        return words + bigrams


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, base_url: str, api_key: str, model_name: str, dimensions: int, timeout_seconds: float) -> None:
        self.provider_name = "openai_compatible"
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model_name
        self.dimensions = dimensions
        self.timeout_seconds = timeout_seconds

    def embed(self, text: str) -> list[float]:
        payload = {"model": self.model_name, "input": text}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url}/embeddings", headers=self._headers(), json=payload)
            response.raise_for_status()
        vector = self._extract_embedding(response.json())
        if self.dimensions > 0 and len(vector) != self.dimensions:
            raise ValueError(f"Embedding model returned {len(vector)} dimensions, expected {self.dimensions}")
        return _normalize(vector)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _extract_embedding(self, payload: dict) -> list[float]:
        data = payload.get("data") or []
        if not data:
            raise ValueError("Embedding response did not include data")
        embedding = data[0].get("embedding") if isinstance(data[0], dict) else None
        if not isinstance(embedding, list) or not all(isinstance(value, (int, float)) for value in embedding):
            raise ValueError("Embedding response did not include a numeric embedding")
        return [float(value) for value in embedding]


def create_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider == "hash":
        return HashEmbeddingProvider()
    if provider in {"openai_compatible", "openai"}:
        missing = [
            name
            for name, value in [
                ("EMBEDDING_BASE_URL", settings.embedding_base_url),
                ("EMBEDDING_API_KEY", settings.embedding_api_key),
                ("EMBEDDING_MODEL", settings.embedding_model),
            ]
            if not value
        ]
        if missing:
            raise ValueError(f"{provider} embedding provider requires: {', '.join(missing)}")
        return OpenAICompatibleEmbeddingProvider(
            settings.embedding_base_url,
            settings.embedding_api_key,
            settings.embedding_model,
            settings.embedding_dimensions,
            settings.embedding_timeout_seconds,
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self.provider = provider or create_embedding_provider()
        self.provider_name = self.provider.provider_name
        self.model_name = self.provider.model_name
        self.dimensions = self.provider.dimensions

    def embed(self, text: str) -> list[float]:
        return self.provider.embed(text)

    def similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        return sum(a * b for a, b in zip(left, right))

    def is_compatible(self, provider_name: str | None, model_name: str | None, dimensions: int | None) -> bool:
        return (
            (provider_name or "hash") == self.provider_name
            and (model_name or "hash-v1") == self.model_name
            and (dimensions or 96) == self.dimensions
        )


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]
