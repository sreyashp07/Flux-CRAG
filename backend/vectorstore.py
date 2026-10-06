"""Persistent local ChromaDB vector store, shared by ingestion and retrieval."""
from functools import lru_cache

from langchain_chroma import Chroma

from backend.config import get_settings
from backend.embeddings import get_embeddings


@lru_cache
def get_vectorstore() -> Chroma:
    settings = get_settings()
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=get_embeddings(),
        persist_directory=str(settings.chroma_dir),
    )
