from langchain_core.documents import Document

from backend.nodes import generator


def _docs():
    return [
        Document(page_content="CRAG grades retrieved documents.", metadata={"source": "crag.md"}),
        Document(
            page_content="Argentina won.",
            metadata={
                "source": "https://x.com",
                "url": "https://x.com",
                "title": "Result",
                "origin": "web",
            },
        ),
    ]


def test_format_context_numbers_each_block():
    context = generator._format_context(_docs())

    assert context.startswith("[1] (crag.md)")
    assert "[2] (Result)" in context


def test_collect_sources_marks_origin_and_location():
    sources = generator._collect_sources(_docs())

    assert [s["origin"] for s in sources] == ["local", "web"]
    assert sources[1]["location"] == "https://x.com"


def test_generate_joins_streamed_tokens(monkeypatch):
    monkeypatch.setattr(
        generator, "_stream_tokens", lambda q, c: iter(["CRAG ", "grades ", "documents."])
    )

    update = generator.generate({"question": "What does CRAG do?", "documents": _docs()})

    assert update == {"generation": "CRAG grades documents."}


def test_generate_without_context_never_calls_llm(monkeypatch):
    def must_not_run(question, context):
        raise AssertionError("LLM must not be called without context")

    monkeypatch.setattr(generator, "_stream_tokens", must_not_run)

    update = generator.generate({"question": "anything", "documents": []})

    assert update["generation"] == generator.NO_CONTEXT_ANSWER


def test_generate_reports_llm_failure(monkeypatch):
    def broken(question, context):
        raise RuntimeError("ollama down")
        yield  # makes this a generator that fails on first iteration

    monkeypatch.setattr(generator, "_stream_tokens", broken)

    update = generator.generate({"question": "q", "documents": _docs()})

    assert update["generation"] == generator.GENERATION_ERROR_ANSWER
