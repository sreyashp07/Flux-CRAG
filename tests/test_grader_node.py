from langchain_core.documents import Document

from backend.config import get_settings
from backend.nodes import grader
from backend.nodes.grader import GradeResult


def _docs():
    return [
        Document(page_content="CRAG evaluates retrieved documents.", metadata={"source": "crag.md"}),
        Document(page_content="Bananas are rich in potassium.", metadata={"source": "fruit.md"}),
    ]


def _fake_grade(question, chunk_text):
    verdict = "yes" if "CRAG" in chunk_text else "no"
    return GradeResult(relevant=verdict, reason="test verdict")


def test_grade_documents_keeps_only_relevant_chunks(monkeypatch):
    monkeypatch.setattr(grader, "_grade_chunk", _fake_grade)

    update = grader.grade_documents({"question": "What is CRAG?", "documents": _docs()})

    assert update["relevance"] == "relevant"
    assert [d.metadata["source"] for d in update["documents"]] == ["crag.md"]
    assert [g["relevant"] for g in update["grades"]] == [True, False]


def test_grade_documents_flags_irrelevant_when_nothing_passes(monkeypatch):
    monkeypatch.setattr(grader, "_grade_chunk", _fake_grade)
    docs = [Document(page_content="Bananas are yellow.", metadata={"source": "fruit.md"})]

    update = grader.grade_documents({"question": "What is CRAG?", "documents": docs})

    assert update["relevance"] == "irrelevant"
    assert update["documents"] == []


def test_grade_documents_handles_empty_document_list(monkeypatch):
    monkeypatch.setattr(grader, "_grade_chunk", _fake_grade)

    update = grader.grade_documents({"question": "What is CRAG?", "documents": []})

    assert update["relevance"] == "irrelevant"
    assert update["grades"] == []


def test_grader_error_counts_as_not_relevant(monkeypatch):
    def boom(question, chunk_text):
        raise RuntimeError("ollama down")

    monkeypatch.setattr(grader, "_grade_chunk", boom)

    update = grader.grade_documents({"question": "What is CRAG?", "documents": _docs()})

    assert update["relevance"] == "irrelevant"
    assert all(g["reason"].startswith("Grader error") for g in update["grades"])


def test_min_relevant_docs_threshold_is_respected(monkeypatch):
    monkeypatch.setattr(grader, "_grade_chunk", _fake_grade)
    monkeypatch.setattr(get_settings(), "min_relevant_docs", 2)

    update = grader.grade_documents({"question": "What is CRAG?", "documents": _docs()})

    assert update["relevance"] == "irrelevant"
