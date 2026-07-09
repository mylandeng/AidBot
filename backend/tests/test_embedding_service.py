import httpx
import pytest

from app.core.config import settings
from app.services.embedding_service import (
    EmbeddingService,
    HashEmbeddingProvider,
    OpenAICompatibleEmbeddingProvider,
    create_embedding_provider,
)


def test_hash_embedding_provider_is_deterministic_and_normalized() -> None:
    provider = HashEmbeddingProvider()

    first = provider.embed("AX-42 App 离线")
    second = provider.embed("AX-42 App 离线")

    assert first == second
    assert len(first) == 96
    assert pytest.approx(sum(value * value for value in first), rel=1e-5) == 1.0


def test_similarity_ignores_mismatched_dimensions() -> None:
    service = EmbeddingService(provider=HashEmbeddingProvider())

    assert service.similarity([1.0, 0.0], [1.0]) == 0.0
    assert service.similarity([1.0, 0.0], []) == 0.0
    assert service.is_compatible("hash", "hash-v1", 96)
    assert not service.is_compatible("openai_compatible", "text-embedding-3-small", 1536)


def test_openai_compatible_embedding_provider_calls_embeddings_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict] = []

    class FakeClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
            return None

        def post(self, url: str, headers: dict[str, str], json: dict) -> httpx.Response:
            calls.append({"url": url, "headers": headers, "json": json, "timeout": self.timeout})
            return httpx.Response(200, json={"data": [{"embedding": [3.0, 4.0]}]}, request=httpx.Request("POST", url))

    monkeypatch.setattr("app.services.embedding_service.httpx.Client", FakeClient)

    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://embedding.example.test/v1/",
        api_key="test-key",
        model_name="test-embedding-model",
        dimensions=2,
        timeout_seconds=12.0,
    )

    vector = provider.embed("售后知识库检索")

    assert vector == [0.6, 0.8]
    assert calls == [
        {
            "url": "https://embedding.example.test/v1/embeddings",
            "headers": {"Authorization": "Bearer test-key", "Content-Type": "application/json"},
            "json": {"model": "test-embedding-model", "input": "售后知识库检索"},
            "timeout": 12.0,
        }
    ]


def test_openai_compatible_embedding_provider_rejects_unexpected_dimensions(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, timeout: float) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
            return None

        def post(self, url: str, headers: dict[str, str], json: dict) -> httpx.Response:
            return httpx.Response(200, json={"data": [{"embedding": [1.0, 0.0, 0.0]}]}, request=httpx.Request("POST", url))

    monkeypatch.setattr("app.services.embedding_service.httpx.Client", FakeClient)
    provider = OpenAICompatibleEmbeddingProvider("https://embedding.example.test/v1", "test-key", "test-model", 2, 12.0)

    with pytest.raises(ValueError, match="expected 2"):
        provider.embed("dimension mismatch")


def test_create_embedding_provider_requires_openai_compatible_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "embedding_provider", "openai_compatible")
    monkeypatch.setattr(settings, "embedding_base_url", "")
    monkeypatch.setattr(settings, "embedding_api_key", "")
    monkeypatch.setattr(settings, "embedding_model", "")

    with pytest.raises(ValueError, match="EMBEDDING_BASE_URL"):
        create_embedding_provider()
