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


def index_documents(chunks: list[Document], reset: bool = False) -> int:
    """Embed and store chunks. Returns the number of unique chunks indexed."""
    store = get_vectorstore()
    if reset:
        store.reset_collection()

    unique: dict[str, Document] = {_chunk_id(c): c for c in chunks}
    if not unique:
        return 0
    store.add_documents(documents=list(unique.values()), ids=list(unique.keys()))
    return len(unique)


def collection_count() -> int:
    """Number of chunks currently stored in the collection."""
    return get_vectorstore()._collection.count()
