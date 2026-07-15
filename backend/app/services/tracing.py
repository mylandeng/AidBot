import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


try:
    import langsmith as _langsmith
except Exception:  # pragma: no cover - local environments may not install optional tracing deps
    _langsmith = None


class _NoopRun:
    def end(self, outputs: dict[str, Any] | None = None) -> None:
        return None


@contextmanager
def trace_run(name: str, run_type: str = "chain", inputs: dict[str, Any] | None = None) -> Iterator[Any]:
    if _langsmith is None:
        yield _NoopRun()
        return

    manager = _langsmith.trace(name, run_type, inputs=inputs or {})
    try:
        run = manager.__enter__()
    except Exception:
        yield _NoopRun()
        return

    try:
        yield run
    except BaseException as exc:
        try:
            manager.__exit__(type(exc), exc, exc.__traceback__)
        except Exception:
            pass
        raise
    else:
        try:
            manager.__exit__(None, None, None)
        except Exception:
            pass


def end_trace(run: Any, outputs: dict[str, Any] | None = None) -> None:
    try:
        run.end(outputs=outputs or {})
    except Exception:
        return


def text_fingerprint(text: str | None) -> dict[str, Any]:
    value = text or ""
    return {
        "length": len(value),
        "sha256_12": hashlib.sha256(value.encode("utf-8")).hexdigest()[:12] if value else "",
    }


def id_fingerprint(value: str | None) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def summarize_user(current_user: Any) -> dict[str, Any]:
    return {
        "user_id_hash": id_fingerprint(getattr(current_user, "id", "")),
        "roles": list(getattr(current_user, "roles", []) or []),
        "auth_method": getattr(current_user, "auth_method", ""),
        "key_id_hash": id_fingerprint(getattr(current_user, "key_id", "")),
    }


def summarize_chat_request(request: Any) -> dict[str, Any]:
    return {
        "question": text_fingerprint(getattr(request, "question", "")),
        "conversation_id_hash": id_fingerprint(getattr(request, "conversation_id", "")),
        "has_conversation_id": bool(getattr(request, "conversation_id", None)),
        "product_line": getattr(request, "product_line", None) or "",
        "retrieval_provider": getattr(request, "retrieval_provider", ""),
    }


def summarize_sources(sources: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(sources),
        "items": [
            {
                "title_hash": id_fingerprint(str(item.get("title") or "")),
                "source_type": item.get("source_type", ""),
                "doc_id": item.get("doc_id", ""),
                "chunk_id": item.get("chunk_id", ""),
                "score": item.get("score", 0),
            }
            for item in sources[:5]
        ],
    }


def summarize_retrieved_chunks(chunks: list[Any]) -> dict[str, Any]:
    items = []
    for item in chunks[:5]:
        citation = item.citation().model_dump()
        items.append(
            {
                "title_hash": id_fingerprint(str(citation.get("title") or "")),
                "source_type": citation.get("source_type", ""),
                "doc_id": citation.get("doc_id", ""),
                "chunk_id": citation.get("chunk_id", ""),
                "score": citation.get("score", 0),
            }
        )
    return {"count": len(chunks), "items": items}


def summarize_chat_response(response: Any) -> dict[str, Any]:
    return {
        "conversation_id_hash": id_fingerprint(getattr(response, "conversation_id", "")),
        "message_id": getattr(response, "message_id", ""),
        "answer": text_fingerprint(getattr(response, "answer", "")),
        "solution_step_count": len(getattr(response, "solution_steps", []) or []),
        "confidence": getattr(response, "confidence", ""),
        "sources": summarize_sources([item.model_dump() if hasattr(item, "model_dump") else item for item in getattr(response, "sources", []) or []]),
        "handoff_required": bool(getattr(response, "handoff_required", False)),
    }


def summarize_llm_completion(completion: Any) -> dict[str, Any]:
    return {
        "answer": text_fingerprint(getattr(completion, "answer", "")),
        "solution_step_count": len(getattr(completion, "solution_steps", []) or []),
        "model_name": getattr(completion, "model_name", ""),
    }


def summarize_exception(exc: BaseException) -> dict[str, str]:
    return {
        "type": exc.__class__.__name__,
        "message": str(exc)[:200],
    }
