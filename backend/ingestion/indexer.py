"""Embed document chunks and persist them in the local ChromaDB collection."""
import hashlib

from langchain_core.documents import Document

from backend.vectorstore import get_vectorstore


def _chunk_id(chunk: Document) -> str:
    """Deterministic ID so re-running ingestion upserts instead of duplicating."""
    key = "|".join(
        [
            str(chunk.metadata.get("source", "")),
            str(chunk.metadata.get("start_index", "")),
            chunk.page_content,
        ]
    )
    return hashlib.sha1(key.encode("utf-8")).hexdigest()
