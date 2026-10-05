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
