"""Local chat model (Ollama) shared by the grader, rewriter and generator nodes."""
from functools import lru_cache

from langchain_ollama import ChatOllama

from backend.config import get_settings


@lru_cache
def get_llm() -> ChatOllama:
    settings = get_settings()
    return ChatOllama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=settings.llm_temperature,
    )
