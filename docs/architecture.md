# Flux-CRAG Architecture

Flux-CRAG implements **Corrective RAG**: retrieved documents are graded for relevance
before generation. If retrieval is weak, the agent rewrites the query and falls back
to web search instead of answering from bad context.

## Agent graph

~~~mermaid
flowchart TD
    A([User Question]) --> B[Retrieve]
    B --> C[Grade Documents]
    C -->|relevant| F[Generate Answer]
    C -->|not relevant| D[Rewrite Query]
    D --> E[Web Search]
    E --> F
    F --> G([Final Answer])
~~~

## Nodes

| Node | Responsibility |
|---|---|
| Retrieve | Similarity search over the local ChromaDB collection |
| Grade Documents | LLM grades each retrieved chunk as relevant or not |
| Rewrite Query | LLM rewrites the question for better search results |
| Web Search | DuckDuckGo fallback when local knowledge is insufficient |
| Generate Answer | LLM answers using only the verified context |

## Runtime

- Everything runs on localhost: Ollama (LLM + embeddings), ChromaDB (vector store), FastAPI (API).
- Each node emits a structured event streamed over SSE to the dashboard UI,
  which highlights the active node in real time.

## Run stream protocol

`backend.runner.stream_run(question)` yields JSON-friendly messages. The CLI,
the API (SSE) and the dashboard all consume this same stream.

| type | fields | meaning |
|---|---|---|
| `run_started` | run_id, question, timestamp | a run began |
| `event` | node, status, message, data, timestamp | a node event |
| `final` | answer, sources, path, relevance, used_web_search | the run finished |
| `error` | message | the run crashed |

### Node event statuses

| status | meaning |
|---|---|
| `started` | the node began working |
| `progress` | per-item update (a graded chunk, or an answer token in `data.token`) |
| `completed` | the node finished; `data` holds its results |
| `decision` | a routing outcome, e.g. "relevance failed, rewriting query" |
| `failed` | the node hit an error but the graph recovered |

### Graph topology

`backend.graph.get_topology()` describes nodes and edges, so the dashboard
draws the state machine from data instead of hard-coding it. The compiled
graph is exported to `graph.mmd` (Mermaid) in this folder.
