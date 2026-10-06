"""Structured events emitted by graph nodes and streamed to the dashboard UI."""
import time
from enum import Enum
from typing import Any


class NodeName(str, Enum):
    """Identifiers for graph nodes; the frontend uses these to highlight the active node."""

    RETRIEVE = "retrieve"
    GRADE = "grade_documents"
    REWRITE = "rewrite_query"
    WEB_SEARCH = "web_search"
    GENERATE = "generate"


class Status(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    DECISION = "decision"  # a routing outcome, e.g. "relevance failed"
    FAILED = "failed"


def build_event(
    node: NodeName,
    status: Status,
    message: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a JSON-serializable event dict."""
    return {
        "node": node.value,
        "status": status.value,
        "message": message,
        "data": data or {},
        "timestamp": time.time(),
    }


def emit(event: dict[str, Any]) -> None:
    """Push an event onto the active LangGraph custom stream.

    Safe to call outside a running graph (for example in unit tests):
    it silently becomes a no-op.
    """
    try:
        from langgraph.config import get_stream_writer

        get_stream_writer()(event)
    except Exception:
        pass
