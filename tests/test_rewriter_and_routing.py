from backend.nodes import rewriter
from backend.routing import route_after_grading


def test_clean_query_strips_quotes_and_extra_lines():
    raw = '"CRAG retrieval evaluator explained"\nExtra commentary'
    assert rewriter._clean_query(raw, "fallback") == "CRAG retrieval evaluator explained"


def test_clean_query_uses_fallback_when_blank():
    assert rewriter._clean_query("  \n ", "fallback") == "fallback"


def test_rewrite_query_updates_search_query(monkeypatch):
    monkeypatch.setattr(rewriter, "_generate_rewrite", lambda q: "2022 FIFA World Cup winner")

    update = rewriter.rewrite_query({"question": "who won the 2022 fifa world cup"})

    assert update == {"search_query": "2022 FIFA World Cup winner"}


def test_rewrite_query_falls_back_to_original_on_llm_error(monkeypatch):
    def boom(question):
        raise RuntimeError("ollama down")

    monkeypatch.setattr(rewriter, "_generate_rewrite", boom)

    update = rewriter.rewrite_query({"question": "original question"})

    assert update == {"search_query": "original question"}


def test_route_goes_to_generate_when_relevant():
    assert route_after_grading({"relevance": "relevant"}) == "generate"


def test_route_goes_to_rewrite_when_irrelevant():
    assert route_after_grading({"relevance": "irrelevant"}) == "rewrite_query"


def test_route_defaults_to_corrective_path_when_relevance_missing():
    assert route_after_grading({}) == "rewrite_query"
