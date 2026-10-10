# Flux-CRAG

Flux-CRAG is an agentic Corrective RAG (CRAG) system built with LangGraph. It runs entirely on your own machine and includes a dashboard that shows the agent's routing decisions live.

A standard RAG pipeline retrieves text and passes it to the language model even when that text is irrelevant. Flux-CRAG grades every retrieved chunk first. If local knowledge is not good enough, the agent rewrites the query, falls back to web search, and only then writes a cited answer.

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [The dashboard](#the-dashboard)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Example run](#example-run)
- [Using your own documents](#using-your-own-documents)
- [Configuration](#configuration)
- [API reference](#api-reference)
- [Project structure](#project-structure)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

## Features

- **Per-chunk relevance grading.** The local LLM returns a structured verdict (relevant or not, with a reason) for every retrieved chunk.
- **Self-correction.** If too few chunks pass grading, the agent rewrites the question into a search-friendly query and uses web search as a fallback.
- **Grounded, cited answers.** The final answer is written only from verified context and cites its sources as [1], [2], and so on. It is streamed token by token.
- **No guessing.** If no usable context exists, the language model is not called. The agent states that it could not find reliable information.
- **Fully local.** The LLM and embeddings run in Ollama, vectors are stored in ChromaDB on disk, and no API keys or cloud services are needed. Web search is the only network call, and only on the fallback path.
- **Observable by design.** Every node emits structured events that are streamed to the dashboard and the command line.
- **Resilient.** Expected failures (offline, empty search results, LLM errors) are reported as events and the run continues instead of crashing.

## Tech stack

| Layer | Technology | Role |
|---|---|---|
| Orchestration | LangGraph, LangChain | State machine with a conditional corrective edge |
| LLM and embeddings | Ollama (`llama3.1:8b`, `nomic-embed-text`) | Grading, rewriting, answering and embedding, all local |
| Vector store | ChromaDB (persistent) | Local similarity search |
| Web fallback | ddgs | Meta-search used when local knowledge is insufficient |
| Backend | FastAPI, Uvicorn, Server-Sent Events | API and live event streaming |
| Frontend | React 18, Vite, Tailwind CSS v4, GSAP, Radix UI | The dashboard |
| Testing | Pytest | 42 tests that need neither Ollama nor internet access |

## How it works

~~~mermaid
flowchart TD
    A([Question]) --> B[Retrieve<br/>top-k chunks from ChromaDB]
    B --> C[Grade<br/>LLM judges every chunk]
    C -->|relevant| G[Generate<br/>cited, streamed answer]
    C -->|irrelevant| D[Rewrite<br/>search-friendly query]
    D --> E[Web search<br/>ddgs fallback]
    E --> G
    G --> H([Answer and sources])
~~~

| Node | Behavior |
|---|---|
| Retrieve | Embeds the question and fetches the top 4 chunks by distance. A lower distance means a closer match. |
| Grade | Asks the LLM for a structured yes or no with a reason for each chunk, and keeps only the relevant ones. A grader error counts as not relevant, so a failing model can never let bad context through. |
| Route | The conditional edge `route_after_grading` goes to Generate when at least `MIN_RELEVANT_DOCS` chunks passed, otherwise into the corrective path. |
| Rewrite | Turns the question into a concise, keyword-rich web query. Falls back to the original question if the LLM fails. |
| Web search | Fetches web results and merges them with any chunks that already passed grading. A network failure is reported as an event and the run continues. |
| Generate | Answers strictly from the numbered context with [n] citations and streams tokens as events. With no context, it skips the LLM call. |

The shared graph state (`GraphState`) holds `question`, `search_query`, `documents`, `grades`, `relevance`, `used_web_search` and `generation`.

Design decisions:

- Ingestion is idempotent. Chunk IDs are content hashes, so running ingest again never creates duplicates.
- The dashboard does not hard-code the graph. It draws the state machine from `GET /api/graph`.
- Events are emitted from inside the nodes through LangGraph's custom stream, so the UI can show "Retrieving..." while the node is still running, not after it finishes.
- The conditional edge is a plain function over the state, so routing is easy to unit test.

## Architecture

~~~mermaid
flowchart LR
    UI[React dashboard] -- "SSE: /api/ask" --> API[FastAPI]
    API --> RUN[runner.stream_run]
    RUN --> LG[LangGraph state machine]
    LG --> OLL[Ollama<br/>LLM and embeddings]
    LG --> CH[(ChromaDB)]
    LG --> WEB[ddgs web search]
    API -- "/api/graph, /api/health, /api/knowledge-base" --> UI
~~~

A single process serves everything. FastAPI exposes the API and also serves the built dashboard from `frontend/dist`.

`backend.runner.stream_run` turns a graph run into a stream of messages. The dashboard, the command-line tool and the API all consume this same stream.

| Message type | Fields | Meaning |
|---|---|---|
| `run_started` | run_id, question, timestamp | A run began |
| `event` | node, status, message, data, timestamp | A node event |
| `final` | answer, sources, path, relevance, used_web_search | The run finished |
| `error` | message | The run crashed |

Node event statuses:

| Status | Meaning |
|---|---|
| `started` | The node began working |
| `progress` | A per-item update, such as a graded chunk, or an answer token in `data.token` |
| `completed` | The node finished; `data` holds its results |
| `decision` | A routing outcome, for example "relevance failed, rewriting query" |
| `failed` | The node hit an error but the graph recovered |

## The dashboard

The dashboard is a React application built with shadcn-style components (Button, Card, Badge, Tabs, ScrollArea) on Radix primitives, styled with Tailwind CSS and animated with GSAP. It uses an olive-green theme with Fraunces and JetBrains Mono fonts, bundled locally so it works offline.

| Panel | What it shows |
|---|---|
| Header | System status, LLM and embedding model, and the number of indexed chunks |
| Command bar | The question input, with preset questions that exercise each route |
| Agent state machine | A live graph: active nodes pulse, a highlight travels along each edge the agent takes, and bypassed nodes dim |
| Run summary | The path taken, the local retrieval verdict, whether web fallback was used, and the elapsed time |
| Grounded answer | The streaming answer with clickable [n] citation chips that highlight their source card, labeled LOCAL or WEB |
| Telemetry tab | Every agent event as a timeline with timestamps |
| Ledger tab | Per-chunk distance bars and grader verdicts with reasons, plus web results |
| Knowledge tab | The indexed documents and their chunk counts |

During a run the dashboard reacts to the event stream as follows:

| Moment in the run | What the dashboard does |
|---|---|
| Retrieve starts | The Retrieve node becomes active and the query is logged in telemetry |
| Grading | Each chunk gets a verdict row in the Ledger tab, with its distance and the grader's reason |
| Relevance fails | The "irrelevant" edge is highlighted toward Rewrite and the decision is logged |
| Rewrite and web search | The rewritten query and the web results appear as those nodes run |
| Generate | The answer streams in, and citation chips link to the source cards |
| Finish | Bypassed nodes dim, and the summary shows the path, web fallback and elapsed time |

## Getting started

### Requirements

- Python 3.12
- Node.js 18 or newer
- [Ollama](https://ollama.com)
- Git

The commands below are for Git Bash on Windows. On Linux or macOS, activate the environment with `source .venv/bin/activate` instead.

### 1. Clone the repository and set up Python

~~~bash
git clone https://github.com/sreyashp07/Flux-CRAG.git
cd Flux-CRAG
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
~~~

### 2. Pull the local models

~~~bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
~~~

### 3. Index the sample knowledge base and verify the setup

~~~bash
python -m scripts.ingest --reset
python -m scripts.healthcheck
~~~

Every line of the health check should show `[ OK ]`.

### 4. Build the dashboard and start the server

~~~bash
cd frontend
npm install
npm run build
cd ..
python -m backend.main
~~~

Open http://127.0.0.1:8000 in your browser.

Every new terminal needs the virtual environment activated first: go to the project folder and run `source .venv/Scripts/activate`.

## Usage

### Dashboard

Type a question in the command bar, or click one of the preset questions, and press Run agent. Watch the state machine, then switch between the Telemetry, Ledger and Knowledge tabs.

### Command line

The same event stream is available in a terminal:

~~~bash
python -m scripts.ask "Who won the 2022 FIFA World Cup?"
~~~

### UI development with hot reload

Run the API and the Vite dev server side by side:

~~~bash
python -m backend.main          # terminal 1: API on port 8000
cd frontend && npm run dev      # terminal 2: UI on port 5173, proxies /api to FastAPI
~~~

Then open http://localhost:5173.

### Suggested questions

| Question | Route | What to look for |
|---|---|---|
| How do conditional edges work in LangGraph? | retrieve, grade, generate | Local chunks are verified and no web fallback is used |
| What does the retrieval evaluator do in CRAG? | retrieve, grade, generate | The answer cites the local CRAG document |
| Who won the 2022 FIFA World Cup? | retrieve, grade, rewrite, web search, generate | All local chunks are rejected, the query is rewritten, and web results are cited |

The first request after starting Ollama is slower because the model must load. Corrective runs make more LLM calls, so allow 30 to 60 seconds on a laptop.

## Example run

This is the output of `python -m scripts.ask "Who won the 2022 FIFA World Cup?"`, lightly abridged. The question is not covered by the local knowledge base, so the agent takes the corrective path.

~~~text
[run 3a696af7] Who won the 2022 FIFA World Cup?

[retrieve       ] started   Retrieving top 4 chunks from local ChromaDB...
[retrieve       ] completed Retrieved 4 chunk(s)
[grade_documents] started   Evaluating relevance of 4 retrieved chunk(s)...
[grade_documents] progress  Chunk 1/4 from corrective_rag_overview.md: not relevant
[grade_documents] progress  Chunk 2/4 from corrective_rag_overview.md: not relevant
[grade_documents] progress  Chunk 3/4 from chromadb_notes.md: not relevant
[grade_documents] progress  Chunk 4/4 from langgraph_concepts.md: not relevant
[grade_documents] decision  Relevance failed (0/4): rewriting query and falling back to web search
[rewrite_query  ] completed Search query: Argentina FIFA World Cup 2022 winner
[web_search     ] completed Fetched 3 web result(s)
[generate       ] started   Generating answer from 3 verified chunk(s)...
Argentina won the 2022 FIFA World Cup, as indicated in the context [2].

------------------------------------------------------------
PATH   : retrieve -> grade_documents -> rewrite_query -> web_search -> generate
WEB    : yes
SOURCE : [1] (web) https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_Final
~~~

## Using your own documents

1. Put `.md` or `.txt` files into `data/documents/`.
2. Re-index with `python -m scripts.ingest --reset`. Use `--docs-dir PATH` to index a different folder.
3. Restart the server so it picks up the new index.

Documents are split by a heading-aware splitter, with a default chunk size of 800 characters and an overlap of 120.

## Configuration

Copy `.env.example` to `.env`. Every setting has a default.

| Variable | Default | Meaning |
|---|---|---|
| `HOST`, `PORT` | `127.0.0.1`, `8000` | Where the server listens |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `LLM_MODEL` | `llama3.1:8b` | Chat model for grading, rewriting and answering |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model |
| `LLM_TEMPERATURE` | `0.0` | Keep at 0 for stable grading |
| `COLLECTION_NAME` | `flux_crag_docs` | ChromaDB collection name |
| `RETRIEVAL_K` | `4` | Chunks fetched per query |
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | `800`, `120` | Chunking used during ingestion |
| `MIN_RELEVANT_DOCS` | `1` | Chunks that must pass grading to skip the corrective path |
| `WEB_SEARCH_MAX_RESULTS` | `3` | Web results fetched on fallback |
| `WEB_SEARCH_BACKEND` | `auto` | ddgs engine: `auto`, `bing`, `yahoo`, `duckduckgo`, `brave`, `google` or `mojeek` |
| `MAX_REWRITE_ATTEMPTS` | `2` | Reserved for a future retry loop; not used yet |

## API reference

Interactive API documentation is available at `/docs` while the server is running.

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Status, models and indexed chunk count |
| `GET /api/graph` | Graph topology (nodes and edges) |
| `GET /api/knowledge-base` | Indexed source files and chunk counts |
| `GET /api/ask?question=...` | Server-Sent Events stream of a run (question up to 500 characters) |

~~~bash
curl http://127.0.0.1:8000/api/health
curl -N "http://127.0.0.1:8000/api/ask?question=How%20do%20conditional%20edges%20work%20in%20LangGraph%3F"
~~~

Each SSE message is named after its type and carries JSON:

~~~text
event: run_started
data: {"type": "run_started", "run_id": "19ad2f48", "question": "...", "timestamp": 1790000000.1}

event: event
data: {"type": "event", "node": "grade_documents", "status": "decision", "message": "Relevance passed (2/4): routing to answer generation", "data": {"relevance": "relevant", "next": "generate"}, "timestamp": 1790000004.2}

event: final
data: {"type": "final", "answer": "...", "sources": [...], "path": ["retrieve", "grade_documents", "generate"], "relevance": "relevant", "used_web_search": false}
~~~

## Project structure

~~~text
Flux-CRAG/
├── backend/
│   ├── api/routes.py        # health, graph, knowledge-base and SSE ask endpoints
│   ├── ingestion/           # loader, chunker, indexer
│   ├── nodes/               # retriever, grader, rewriter, web_search, generator
│   ├── config.py            # typed settings loaded from .env
│   ├── embeddings.py        # Ollama embeddings
│   ├── events.py            # event vocabulary and safe emitter
│   ├── graph.py             # LangGraph assembly and topology
│   ├── llm.py               # Ollama chat model
│   ├── main.py              # FastAPI app, also serves the dashboard
│   ├── prompts.py           # grader, rewriter and generator prompts
│   ├── routing.py           # conditional edge
│   ├── runner.py            # stream_run: turns a graph run into a message stream
│   ├── state.py             # GraphState
│   └── vectorstore.py       # persistent ChromaDB store
├── frontend/
│   └── src/                 # components, hooks, lib, styles
├── data/documents/          # knowledge base source files
├── docs/                    # architecture notes and exported graph diagram
├── scripts/                 # ingest, healthcheck, ask
├── tests/                   # test suite
├── .env.example
├── requirements.txt
└── README.md
~~~

## Testing

~~~bash
python -m pytest -q
~~~

The suite has 42 tests and needs neither Ollama nor internet access. It covers ingestion, the retriever, the grader (including error safety and the relevance threshold), the rewriter, routing, web search resilience, the generator's no-context guard, the compiled graph's topology, the runner's end-to-end routing with fake nodes, the API endpoints, SSE streaming and dashboard serving.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No module named pydantic_settings` or a similar import error | The virtual environment is not active. Run `source .venv/Scripts/activate`. |
| `Could not find platform independent libraries` or `No module named pip` | A broken system Python is being used. Recreate the environment with Python 3.12: `py -3.12 -m venv .venv`. |
| Web search returns nothing, or `DDGSException` | Search engines vary by network. Set `WEB_SEARCH_BACKEND=bing` (or `yahoo`) in `.env`. Only a single engine name is accepted, not a comma-separated list. |
| `Cannot reach Ollama` | Start the Ollama app, then run `python -m scripts.healthcheck`. |
| The root page says the dashboard is not built | Run `cd frontend && npm install && npm run build`. |
| Port 8000 is already in use | Change `PORT` in `.env`. |
| An answer cites a weak web source | Small local models choose citations imperfectly. See the roadmap. |

## Roadmap

- Grade web results as well, and rank trusted domains first
- Retry loop using `MAX_REWRITE_ATTEMPTS`
- PDF ingestion
- Multi-turn conversation memory
- Retrieval evaluation harness with a labeled question set
