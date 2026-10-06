from langchain_core.documents import Document

from backend.config import get_settings
from backend.nodes import retriever


class FakeStore:
    def __init__(self):
        self.calls = []

    def similarity_search_with_score(self, query, k):
        self.calls.append((query, k))
        return [
            (Document(page_content="Chunk about the CRAG evaluator.", metadata={"source": "a.md"}), 0.42),
            (Document(page_content="Another chunk.", metadata={"source": "b.md"}), 0.9),
        ]


def test_retrieve_returns_documents_with_distance(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(retriever, "get_vectorstore", lambda: store)

    update = retriever.retrieve({"question": "What is CRAG?"})

    assert update["search_query"] == "What is CRAG?"
    assert [d.metadata["distance"] for d in update["documents"]] == [0.42, 0.9]
    assert store.calls == [("What is CRAG?", get_settings().retrieval_k)]


def test_retrieve_prefers_rewritten_search_query(monkeypatch):
    store = FakeStore()
    monkeypatch.setattr(retriever, "get_vectorstore", lambda: store)

    update = retriever.retrieve({"question": "original", "search_query": "rewritten"})

    assert update["search_query"] == "rewritten"
    assert store.calls[0][0] == "rewritten"
