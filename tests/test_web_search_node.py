from langchain_core.documents import Document

from backend.nodes import web_search

FAKE_RESULTS = [
    {
        "title": "FIFA World Cup 2022",
        "href": "https://example.com/wc",
        "body": "Argentina won the 2022 World Cup.",
    },
    {"title": "Empty result", "href": "https://example.com/empty", "body": "   "},
]


def test_to_documents_maps_fields_and_skips_empty_bodies():
    docs = web_search._to_documents(FAKE_RESULTS)

    assert len(docs) == 1
    assert docs[0].metadata == {
        "source": "https://example.com/wc",
        "url": "https://example.com/wc",
        "title": "FIFA World Cup 2022",
        "origin": "web",
    }
    assert "Argentina won" in docs[0].page_content


def test_web_search_combines_with_existing_documents(monkeypatch):
    monkeypatch.setattr(web_search, "_search_web", lambda query, n: FAKE_RESULTS)
    existing = [Document(page_content="local chunk", metadata={"source": "a.md"})]

    update = web_search.web_search(
        {"question": "q", "search_query": "rewritten", "documents": existing}
    )

    assert update["used_web_search"] is True
    assert [d.metadata["source"] for d in update["documents"]] == [
        "a.md",
        "https://example.com/wc",
    ]


def test_web_search_prefers_rewritten_query(monkeypatch):
    seen = {}

    def fake_search(query, n):
        seen["query"] = query
        return []

    monkeypatch.setattr(web_search, "_search_web", fake_search)

    web_search.web_search({"question": "original", "search_query": "rewritten"})

    assert seen["query"] == "rewritten"


def test_web_search_survives_network_failure(monkeypatch):
    def boom(query, n):
        raise RuntimeError("offline")

    monkeypatch.setattr(web_search, "_search_web", boom)

    update = web_search.web_search({"question": "q"})

    assert update == {"documents": [], "used_web_search": True}
