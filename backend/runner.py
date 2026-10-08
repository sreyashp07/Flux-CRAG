"""Runs the graph and turns its execution into a stream of JSON-friendly messages.

Message types yielded by `stream_run`:
    run_started  - the run began
    event        - a node event (started / progress / completed / decision / failed)
    final        - the finished answer, sources and the path the agent took
    error        - the run crashed
"""
import time
from collections.abc import Iterator
from uuid import uuid4

from backend.graph import get_graph
from backend.nodes.generator import _collect_sources as collect_sources


def stream_run(question: str) -> Iterator[dict]:
    run_id = uuid4().hex[:8]
    yield {"type": "run_started", "run_id": run_id, "question": question, "timestamp": time.time()}

    state: dict = {"question": question}
    path: list[str] = []

    try:
        for mode, chunk in get_graph().stream(state, stream_mode=["custom", "updates"]):
            if mode == "custom":
                yield {"type": "event", **chunk}
            elif mode == "updates":
                for node_name, update in chunk.items():
                    path.append(node_name)
                    state.update(update or {})
    except Exception as exc:
        yield {"type": "error", "run_id": run_id, "message": f"{exc.__class__.__name__}: {exc}"}
        return

    yield {
        "type": "final",
        "run_id": run_id,
        "answer": state.get("generation", ""),
        "sources": collect_sources(state.get("documents", [])),
        "path": path,
        "relevance": state.get("relevance"),
        "used_web_search": state.get("used_web_search", False),
        "timestamp": time.time(),
    }
