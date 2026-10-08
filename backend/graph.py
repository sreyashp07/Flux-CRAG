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


def build_graph():
    """Wire nodes and edges into a compiled, runnable LangGraph.

    START -> retrieve -> grade --relevant--> generate -> END
                           \\--irrelevant--> rewrite -> web_search -> generate
    """
    workflow = StateGraph(GraphState)

    workflow.add_node(RETRIEVE, retrieve)
    workflow.add_node(GRADE, grade_documents)
    workflow.add_node(REWRITE, rewrite_query)
    workflow.add_node(WEB_SEARCH, web_search)
    workflow.add_node(GENERATE, generate)

    workflow.add_edge(START, RETRIEVE)
    workflow.add_edge(RETRIEVE, GRADE)
    workflow.add_conditional_edges(
        GRADE,
        route_after_grading,
        {GENERATE: GENERATE, REWRITE: REWRITE},
    )
    workflow.add_edge(REWRITE, WEB_SEARCH)
    workflow.add_edge(WEB_SEARCH, GENERATE)
    workflow.add_edge(GENERATE, END)

    return workflow.compile()


@lru_cache
def get_graph():
    """Compile once and reuse across requests."""
    return build_graph()
