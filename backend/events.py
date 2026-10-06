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
