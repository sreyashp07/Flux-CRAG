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
