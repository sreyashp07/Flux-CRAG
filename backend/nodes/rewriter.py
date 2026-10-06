"""Rewriter node: turn a question that failed retrieval into a search-friendly web query."""
from langchain_core.output_parsers import StrOutputParser

from backend.events import NodeName, Status, build_event, emit
from backend.llm import get_llm
from backend.prompts import REWRITER_PROMPT
from backend.state import GraphState


def _generate_rewrite(question: str) -> str:
    """Ask the local LLM for a rewritten, keyword-rich query."""
    chain = REWRITER_PROMPT | get_llm() | StrOutputParser()
    return chain.invoke({"question": question})


def _clean_query(raw: str, fallback: str) -> str:
    """Take the first non-empty line and strip wrapping quotes; fall back if blank."""
    for line in raw.strip().splitlines():
        cleaned = line.strip().strip("\"'").strip()
        if cleaned:
            return cleaned
    return fallback


def rewrite_query(state: GraphState) -> dict:
    """LangGraph node: replace `search_query` with a web-search-optimised rewrite."""
    question = state["question"]

    emit(
        build_event(
            NodeName.REWRITE,
            Status.STARTED,
            "Relevance failed: rewriting query for web search...",
            {"original": question},
        )
    )

    try:
        rewritten = _clean_query(_generate_rewrite(question), fallback=question)
    except Exception as exc:  # keep the pipeline alive even if the LLM hiccups
        rewritten = question
        emit(
            build_event(
                NodeName.REWRITE,
                Status.FAILED,
                f"Rewrite failed ({exc.__class__.__name__}); keeping the original query",
                {"error": str(exc)},
            )
        )

    emit(
        build_event(
            NodeName.REWRITE,
            Status.COMPLETED,
            f"Search query: {rewritten}",
            {"original": question, "rewritten": rewritten},
        )
    )

    return {"search_query": rewritten}
