from langchain_core.documents import Document

from backend import graph as graph_module
from backend import runner
from backend.events import NodeName, Status, build_event, emit


def _fake_generate(state):
    emit(build_event(NodeName.GENERATE, Status.COMPLETED, "Answer ready", {"answer": "final answer"}))
    return {"generation": "final answer"}


def _install_fake_nodes(monkeypatch, relevance):
    web_doc = Document(
        page_content="Argentina won.",
        metadata={"source": "https://x.com", "url": "https://x.com", "title": "Result", "origin": "web"},
    )
    monkeypatch.setattr(graph_module, "retrieve", lambda s: {"search_query": s["question"], "documents": []})
    monkeypatch.setattr(graph_module, "grade_documents", lambda s: {"relevance": relevance, "grades": []})
    monkeypatch.setattr(graph_module, "rewrite_query", lambda s: {"search_query": "rewritten"})
    monkeypatch.setattr(
        graph_module, "web_search", lambda s: {"documents": [web_doc], "used_web_search": True}
    )
    monkeypatch.setattr(graph_module, "generate", _fake_generate)
    monkeypatch.setattr(runner, "get_graph", graph_module.build_graph)


def test_relevant_path_skips_the_corrective_nodes(monkeypatch):
    _install_fake_nodes(monkeypatch, "relevant")

    items = list(runner.stream_run("What is CRAG?"))
    final = items[-1]

    assert items[0]["type"] == "run_started"
    assert final["type"] == "final"
    assert final["path"] == ["retrieve", "grade_documents", "generate"]
    assert final["answer"] == "final answer"
    assert final["used_web_search"] is False
    assert any(i["type"] == "event" and i["node"] == "generate" for i in items)


def test_irrelevant_path_takes_rewrite_then_web_search(monkeypatch):
    _install_fake_nodes(monkeypatch, "irrelevant")

    final = list(runner.stream_run("Who won the 2022 World Cup?"))[-1]

    assert final["path"] == ["retrieve", "grade_documents", "rewrite_query", "web_search", "generate"]
    assert final["used_web_search"] is True
    assert final["sources"][0]["origin"] == "web"


def test_node_crash_becomes_an_error_message(monkeypatch):
    _install_fake_nodes(monkeypatch, "relevant")

    def boom(state):
        raise RuntimeError("boom")

    monkeypatch.setattr(graph_module, "generate", boom)

    items = list(runner.stream_run("anything"))

    assert items[-1]["type"] == "error"
    assert "boom" in items[-1]["message"]
    assert all(i["type"] != "final" for i in items)
