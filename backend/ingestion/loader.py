"""Load raw source documents from disk into LangChain Documents."""
from pathlib import Path

from langchain_core.documents import Document

from backend.config import get_settings

SUPPORTED_EXTENSIONS = {".txt", ".md"}
