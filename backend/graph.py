"""Assembles the Flux-CRAG LangGraph state machine."""
from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from backend.events import NodeName
from backend.nodes.generator import generate
from backend.nodes.grader import grade_documents
from backend.nodes.retriever import retrieve
from backend.nodes.rewriter import rewrite_query
from backend.nodes.web_search import web_search
from backend.routing import route_after_grading
from backend.state import GraphState

RETRIEVE = NodeName.RETRIEVE.value
GRADE = NodeName.GRADE.value
REWRITE = NodeName.REWRITE.value
WEB_SEARCH = NodeName.WEB_SEARCH.value
GENERATE = NodeName.GENERATE.value


def get_topology() -> dict:
    """Describe the graph for the dashboard so the UI never hard-codes it."""
    return {
        "nodes": [
            {"id": RETRIEVE, "label": "Retrieve", "description": "Similarity search over local ChromaDB"},
            {"id": GRADE, "label": "Grade", "description": "LLM relevance check on every chunk"},
            {"id": REWRITE, "label": "Rewrite", "description": "Optimise the query for web search"},
            {"id": WEB_SEARCH, "label": "Web Search", "description": "DuckDuckGo fallback"},
            {"id": GENERATE, "label": "Generate", "description": "Cited answer from verified context"},
        ],
        "edges": [
            {"source": RETRIEVE, "target": GRADE, "conditional": False},
            {"source": GRADE, "target": GENERATE, "conditional": True, "label": "relevant"},
            {"source": GRADE, "target": REWRITE, "conditional": True, "label": "irrelevant"},
            {"source": REWRITE, "target": WEB_SEARCH, "conditional": False},
            {"source": WEB_SEARCH, "target": GENERATE, "conditional": False},
        ],
    }
