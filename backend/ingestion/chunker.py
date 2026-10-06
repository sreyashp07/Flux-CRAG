"""Split loaded documents into overlapping chunks suitable for embedding."""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import get_settings


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """Split documents on markdown headings, paragraphs, then sentences.

    Every chunk keeps its parent's metadata plus a `start_index` offset,
    which later lets the UI show exactly where a retrieved passage came from.
    """
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size if chunk_size is None else chunk_size,
        chunk_overlap=settings.chunk_overlap if chunk_overlap is None else chunk_overlap,
        add_start_index=True,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)
