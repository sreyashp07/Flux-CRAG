# LangGraph Core Concepts

LangGraph is a library for building stateful, multi-step agent workflows as
graphs. Instead of a single linear chain, an agent is described as nodes and
edges, which makes branching, loops and retries explicit.

## State

A graph shares a single state object between all nodes. The state is usually
a TypedDict, and each node receives the current state and returns a partial
update. Reducers control how updates merge, for example appending to a list
instead of overwriting it.

## Nodes and edges

Nodes are plain Python functions that do the work, such as retrieving
documents or calling a language model. Edges connect nodes in order. The
special START and END markers mark where the graph begins and finishes.

## Conditional edges

A conditional edge uses a routing function that inspects the state and returns
the name of the next node. This is how an agent decides, for instance, whether
to generate an answer or to rewrite the query and search the web.

## Compiling

After nodes and edges are added to a StateGraph, calling compile produces a
runnable graph that can be invoked or streamed step by step.
