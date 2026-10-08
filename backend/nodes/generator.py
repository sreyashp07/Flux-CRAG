"""Generator node: answer strictly from verified context, streaming tokens to the dashboard."""
from collections.abc import Iterator

from backend.events import NodeName, Status, build_event, emit
from backend.llm import get_llm
from backend.prompts import GENERATOR_PROMPT
from backend.state import GraphState

NO_CONTEXT_ANSWER = (
    "I could not find reliable information to answer this question, "
    "either in the local knowledge base or on the web."
)
GENERATION_ERROR_ANSWER = (
    "Answer generation failed because the local LLM did not respond. "
    "Check that Ollama is running and try again."
)


def _format_context(documents: list) -> str:
    """Number each chunk so the LLM can cite it as [1], [2], ..."""
    blocks = []
    for index, doc in enumerate(documents, start=1):
        label = doc.metadata.get("title") or doc.metadata.get("source", "unknown")
        blocks.append(f"[{index}] ({label})\n{doc.page_content}")
    return "\n\n".join(blocks)


def _collect_sources(documents: list) -> list[dict]:
    """Describe each context chunk for the dashboard's citation panel."""
    sources = []
    for index, doc in enumerate(documents, start=1):
        meta = doc.metadata
        sources.append(
            {
                "id": index,
                "origin": meta.get("origin", "local"),
                "title": meta.get("title") or meta.get("source", "unknown"),
                "location": meta.get("url") or meta.get("source", "unknown"),
            }
        )
    return sources


def _stream_tokens(question: str, context: str) -> Iterator[str]:
    """Stream the answer token by token from the local LLM."""
    chain = GENERATOR_PROMPT | get_llm()
    for chunk in chain.stream({"context": context, "question": question}):
        token = str(chunk.content)
        if token:
            yield token
