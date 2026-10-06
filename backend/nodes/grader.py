"""Grader node: LLM-based relevance check on each retrieved chunk (the 'corrective' step of CRAG)."""
from typing import Literal

from pydantic import BaseModel, Field

from backend.config import get_settings
from backend.events import NodeName, Status, build_event, emit
from backend.llm import get_llm
from backend.prompts import GRADER_PROMPT
from backend.state import GraphState


class GradeResult(BaseModel):
    """Structured verdict returned by the grading LLM."""

    relevant: Literal["yes", "no"] = Field(
        description="'yes' if the chunk helps answer the question, otherwise 'no'"
    )
    reason: str = Field(description="One short sentence justifying the verdict")


def _grade_chunk(question: str, chunk_text: str) -> GradeResult:
    """Ask the local LLM for a structured relevance verdict on one chunk."""
    chain = GRADER_PROMPT | get_llm().with_structured_output(GradeResult)
    return chain.invoke({"question": question, "document": chunk_text})


def grade_documents(state: GraphState) -> dict:
    """LangGraph node: grade every retrieved chunk, keep only the relevant ones.

    Sets `relevance` to "relevant" when at least `min_relevant_docs` chunks pass,
    otherwise "irrelevant" (which routes the graph into the corrective path).
    """
    settings = get_settings()
    question = state["question"]
    documents = state.get("documents", [])
    total = len(documents)

    emit(
        build_event(
            NodeName.GRADE,
            Status.STARTED,
            f"Evaluating relevance of {total} retrieved chunk(s)...",
            {"total": total},
        )
    )

    grades: list[dict] = []
    relevant_docs = []
    for index, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown")
        try:
            result = _grade_chunk(question, doc.page_content)
            is_relevant, reason = result.relevant == "yes", result.reason
        except Exception as exc:  # a flaky grader must never let bad context through
            is_relevant, reason = False, f"Grader error: {exc.__class__.__name__}"

        grade = {"source": source, "relevant": is_relevant, "reason": reason}
        grades.append(grade)
        if is_relevant:
            relevant_docs.append(doc)

        verdict = "relevant" if is_relevant else "not relevant"
        emit(
            build_event(
                NodeName.GRADE,
                Status.PROGRESS,
                f"Chunk {index}/{total} from {source}: {verdict}",
                {"index": index, "total": total, **grade},
            )
        )

    passed = len(relevant_docs) >= settings.min_relevant_docs
    relevance = "relevant" if passed else "irrelevant"

    emit(
        build_event(
            NodeName.GRADE,
            Status.COMPLETED,
            f"Graded {total} chunk(s): {len(relevant_docs)} relevant",
            {"grades": grades, "relevant_count": len(relevant_docs), "total": total},
        )
    )

    if passed:
        message = f"Relevance passed ({len(relevant_docs)}/{total}): routing to answer generation"
        next_node = NodeName.GENERATE.value
    else:
        message = (
            f"Relevance failed ({len(relevant_docs)}/{total}): "
            "rewriting query and falling back to web search"
        )
        next_node = NodeName.REWRITE.value

    emit(
        build_event(
            NodeName.GRADE,
            Status.DECISION,
            message,
            {"relevance": relevance, "next": next_node},
        )
    )

    return {"grades": grades, "relevance": relevance, "documents": relevant_docs}
