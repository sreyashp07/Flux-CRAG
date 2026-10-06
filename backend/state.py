"""LangGraph state definition shared by every node in the Flux-CRAG graph."""
from typing import Literal, TypedDict

from langchain_core.documents import Document


class GraphState(TypedDict, total=False):
    """Single state object that flows through every node of the graph.

    Nodes return partial updates; LangGraph merges them into this state.
    """

    # --- Input ---
    question: str  # the user's original question

    # --- Retrieval ---
    search_query: str  # working query; starts as the question, replaced by the rewriter
    documents: list[Document]  # context chunks (from ChromaDB or web search)

    # --- Grading ---
    grades: list[dict]  # per-document verdicts: {"source", "relevant", "reason"}
    relevance: Literal["relevant", "irrelevant"]  # overall verdict used for routing

    # --- Control flow ---
    used_web_search: bool  # True once the web fallback has been taken

    # --- Output ---
    generation: str  # final answer
