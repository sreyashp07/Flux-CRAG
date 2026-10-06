"""Load raw source documents from disk into LangChain Documents."""
from pathlib import Path

from langchain_core.documents import Document

from backend.config import get_settings

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_documents(docs_dir: Path | None = None) -> list[Document]:
    """Recursively load every supported file under docs_dir.

    Each file becomes one Document whose metadata records its relative path
    (`source`) and extension (`file_type`). Empty files are skipped.
    """
    root = Path(docs_dir) if docs_dir else get_settings().docs_dir
    if not root.exists():
        raise FileNotFoundError(f"Documents directory not found: {root}")

    documents: list[Document] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": path.relative_to(root).as_posix(),
                    "file_type": path.suffix.lower().lstrip("."),
                },
            )
        )
    return documents
