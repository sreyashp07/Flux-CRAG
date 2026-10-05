# Flux-CRAG

Agentic **Corrective RAG** system built with **LangGraph**, running 100% on localhost.
A custom dashboard visualizes the agent's internal decisions live:
`Retrieving -> Evaluating relevance -> Rewriting query -> Web search fallback -> Generating`.

## Stack

- **Orchestration:** LangGraph
- **LLM + embeddings:** Ollama (llama3.1:8b, nomic-embed-text)
- **Vector store:** ChromaDB (local, persistent)
- **Web fallback:** DuckDuckGo (ddgs)
- **Backend:** FastAPI + Server-Sent Events
- **Frontend:** Vanilla HTML/CSS/JS dashboard

## Quick start

    git clone https://github.com/sreyashp07/Flux-CRAG.git
    cd Flux-CRAG
    python -m venv .venv
    source .venv/Scripts/activate      # Linux/macOS: source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    ollama pull llama3.1:8b
    ollama pull nomic-embed-text

## Project layout

    backend/     FastAPI app, LangGraph state/graph, nodes, ingestion
    frontend/    Dashboard UI
    data/        Source documents (and generated local vector store)
    scripts/     CLI helpers
    tests/       Test suite
    docs/        Architecture documentation

See [docs/architecture.md](docs/architecture.md) for the agent graph.

## Status

Under active development, built in stages.
