"""Retriever node: fetch the top-k most similar chunks from the local ChromaDB store."""
from backend.config import get_settings
from backend.events import NodeName, Status, build_event, emit
from backend.state import GraphState
from backend.vectorstore import get_vectorstore

PREVIEW_CHARS = 160
