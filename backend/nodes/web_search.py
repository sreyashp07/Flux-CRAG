"""Web search node: DuckDuckGo fallback used when local retrieval fails the relevance check."""
from ddgs import DDGS
from langchain_core.documents import Document

from backend.config import get_settings
from backend.events import NodeName, Status, build_event, emit
from backend.state import GraphState

SNIPPET_PREVIEW_CHARS = 160


def _search_web(query: str, max_results: int) -> list[dict]:
    """Run a DuckDuckGo text search. Returns dicts with title, href and body keys."""
    return list(DDGS().text(query, max_results=max_results))


def _to_documents(results: list[dict]) -> list[Document]:
    """Convert raw search hits into Documents tagged with origin='web'."""
    documents = []
    for result in results:
        body = (result.get("body") or "").strip()
        if not body:
            continue
        url = result.get("href", "")
        title = result.get("title") or url
        documents.append(
            Document(
                page_content=f"{title}\n{body}",
                metadata={"source": url, "url": url, "title": title, "origin": "web"},
            )
        )
    return documents
