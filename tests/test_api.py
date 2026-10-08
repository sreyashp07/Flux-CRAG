import json

from fastapi.testclient import TestClient

from backend.api import routes
from backend.main import create_app

client = TestClient(create_app())


class FakeStore:
    def get(self, include=None):
        return {"metadatas": [{"source": "a.md"}, {"source": "a.md"}, {"source": "b.md"}]}


def _parse_sse(text):
    messages = []
    for block in text.replace("\r\n", "\n").split("\n\n"):
        fields = dict(line.split(": ", 1) for line in block.split("\n") if ": " in line)
        if "event" in fields:
            messages.append((fields["event"], json.loads(fields["data"])))
    return messages


def test_health_reports_ok_and_chunk_count(monkeypatch):
    monkeypatch.setattr(routes, "collection_count", lambda: 5)

    body = client.get("/api/health").json()

    assert body["status"] == "ok"
    assert body["chunks_indexed"] == 5


def test_health_degrades_when_store_is_unavailable(monkeypatch):
    def broken():
        raise RuntimeError("chroma missing")

    monkeypatch.setattr(routes, "collection_count", broken)

    body = client.get("/api/health").json()

    assert body["status"] == "degraded"
    assert body["chunks_indexed"] is None


def test_graph_endpoint_returns_topology():
    body = client.get("/api/graph").json()

    assert len(body["nodes"]) == 5
    assert {"source": "retrieve", "target": "grade_documents", "conditional": False} in body["edges"]


def test_knowledge_base_counts_chunks_per_source(monkeypatch):
    monkeypatch.setattr(routes, "get_vectorstore", lambda: FakeStore())

    body = client.get("/api/knowledge-base").json()

    assert body["total_chunks"] == 3
    assert body["sources"] == [
        {"source": "a.md", "chunks": 2},
        {"source": "b.md", "chunks": 1},
    ]


def test_ask_rejects_empty_and_oversized_questions():
    for question in ["", "   ", "x" * 501]:
        assert client.get("/api/ask", params={"question": question}).status_code == 422


def test_ask_streams_runner_messages_as_sse(monkeypatch):
    def fake_stream(question):
        yield {"type": "run_started", "run_id": "r1", "question": question}
        yield {"type": "event", "node": "retrieve", "status": "started", "message": "Retrieving...", "data": {}}
        yield {"type": "final", "answer": "ok", "sources": [], "path": ["retrieve"]}

    monkeypatch.setattr(routes, "stream_run", fake_stream)

    response = client.get("/api/ask", params={"question": "What is CRAG?"})
    messages = _parse_sse(response.text)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert [name for name, _ in messages] == ["run_started", "event", "final"]
    assert messages[0][1]["question"] == "What is CRAG?"
