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
