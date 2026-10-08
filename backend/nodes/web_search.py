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


def web_search(state: GraphState) -> dict:
    """LangGraph node: fetch web results and merge them with any chunks that already passed grading.

    Network failures never crash the graph: the node reports a FAILED event and
    returns whatever context already exists.
    """
    settings = get_settings()
    query = state.get("search_query") or state["question"]
    existing = state.get("documents", [])

    emit(
        build_event(
            NodeName.WEB_SEARCH,
            Status.STARTED,
            "Web search fallback: querying DuckDuckGo...",
            {"query": query},
        )
    )

    try:
        web_docs = _to_documents(_search_web(query, settings.web_search_max_results))
    except Exception as exc:  # offline, rate-limited, etc.
        web_docs = []
        emit(
            build_event(
                NodeName.WEB_SEARCH,
                Status.FAILED,
                f"Web search failed ({exc.__class__.__name__})",
                {"error": str(exc)},
            )
        )

    emit(
        build_event(
            NodeName.WEB_SEARCH,
            Status.COMPLETED,
            f"Fetched {len(web_docs)} web result(s)",
            {
                "count": len(web_docs),
                "results": [
                    {
                        "title": d.metadata["title"],
                        "url": d.metadata["url"],
                        "snippet": d.page_content[:SNIPPET_PREVIEW_CHARS].replace("\n", " "),
                    }
                    for d in web_docs
                ],
            },
        )
    )

    return {"documents": existing + web_docs, "used_web_search": True}
