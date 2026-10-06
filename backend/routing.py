"""Conditional-edge routing functions for the Flux-CRAG graph."""
from backend.events import NodeName
from backend.state import GraphState


def route_after_grading(state: GraphState) -> str:
    """Decide the next node once documents have been graded.

    Enough relevant chunks -> answer directly.
    Otherwise -> take the corrective path (rewrite the query, then web search).
    """
    if state.get("relevance") == "relevant":
        return NodeName.GENERATE.value
    return NodeName.REWRITE.value
