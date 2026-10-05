"""Central, typed configuration for Flux-CRAG.

All values can be overridden through environment variables or a local `.env` file.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Server ---
    app_name: str = "Flux-CRAG"
    host: str = "127.0.0.1"
    port: int = 8000

    # --- Local LLM (Ollama) ---
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.1:8b"
    embedding_model: str = "nomic-embed-text"
    llm_temperature: float = 0.0

    # --- Storage ---
    chroma_dir: Path = BASE_DIR / "data" / "chroma"
    docs_dir: Path = BASE_DIR / "data" / "documents"
    collection_name: str = "flux_crag_docs"

    # --- Retrieval ---
    retrieval_k: int = 4

    # --- Corrective RAG behaviour ---
    min_relevant_docs: int = 1
    max_rewrite_attempts: int = 2
    web_search_max_results: int = 3


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
