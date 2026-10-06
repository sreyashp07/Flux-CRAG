"""Retriever node: fetch the top-k most similar chunks from the local ChromaDB store."""
from backend.config import get_settings
from backend.events import NodeName, Status, build_event, emit
from backend.state import GraphState
from backend.vectorstore import get_vectorstore

PREVIEW_CHARS = 160


def retrieve(state: GraphState) -> dict:
    """LangGraph node: similarity search, attaching each chunk's distance score.

    Uses the rewritten `search_query` when present, otherwise the raw question.
    Lower distance means a closer match.
    """
    settings = get_settings()
    query = state.get("search_query") or state["question"]

    emit(
        build_event(
            NodeName.RETRIEVE,
            Status.STARTED,
            f"Retrieving top {settings.retrieval_k} chunks from local ChromaDB...",
            {"query": query},
        )
    )

    results = get_vectorstore().similarity_search_with_score(query, k=settings.retrieval_k)

    documents = []
    for doc, distance in results:
        doc.metadata["distance"] = float(distance)
        documents.append(doc)

    emit(
        build_event(
            NodeName.RETRIEVE,
            Status.COMPLETED,
            f"Retrieved {len(documents)} chunk(s)",
            {
                "count": len(documents),
                "chunks": [
                    {
                        "source": d.metadata.get("source", "unknown"),
                        "distance": round(d.metadata["distance"], 4),
                        "preview": d.page_content[:PREVIEW_CHARS].replace("\n", " "),
                    }
                    for d in documents
                ],
            },
        )
    )

    return {"search_query": query, "documents": documents}
