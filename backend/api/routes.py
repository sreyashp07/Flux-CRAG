"""HTTP routes: health, graph topology, knowledge-base stats and the streaming ask endpoint."""
import json

from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from backend.config import get_settings
from backend.graph import get_topology
from backend.ingestion.indexer import collection_count
from backend.runner import stream_run
from backend.vectorstore import get_vectorstore

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    """Liveness plus the models and index size shown in the dashboard header."""
    settings = get_settings()
    try:
        chunks = collection_count()
        status = "ok"
    except Exception:
        chunks = None
        status = "degraded"
    return {
        "status": status,
        "app": settings.app_name,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "chunks_indexed": chunks,
    }


@router.get("/graph")
def graph() -> dict:
    """Nodes and edges of the agent graph, so the UI never hard-codes them."""
    return get_topology()


@router.get("/knowledge-base")
def knowledge_base() -> dict:
    """Which source files are indexed and how many chunks each contributed."""
    data = get_vectorstore().get(include=["metadatas"])
    counts: dict[str, int] = {}
    for metadata in data.get("metadatas") or []:
        source = (metadata or {}).get("source", "unknown")
        counts[source] = counts.get(source, 0) + 1
    return {
        "total_chunks": sum(counts.values()),
        "sources": [{"source": name, "chunks": n} for name, n in sorted(counts.items())],
    }
