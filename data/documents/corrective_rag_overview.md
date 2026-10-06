# Corrective RAG (CRAG) Overview

Corrective Retrieval Augmented Generation (CRAG) is a technique that adds a
self-check step to standard RAG. A basic RAG pipeline retrieves documents and
passes them straight to the language model, even when they are irrelevant.
CRAG evaluates the retrieved documents first and corrects course when
retrieval quality is poor.

## Retrieval evaluator

The core of CRAG is a lightweight retrieval evaluator that scores how relevant
each retrieved document is to the question. Based on the scores, the system
chooses one of three actions: use the documents as they are (correct), discard
them and search elsewhere (incorrect), or combine both sources (ambiguous).

## Web search fallback

When the local knowledge base cannot answer a question, CRAG falls back to web
search. The question is often rewritten into a search-friendly query first, so
the web results are more likely to be useful.

## Knowledge refinement

CRAG also filters retrieved content down to the most relevant passages before
generation, which reduces noise and lowers the chance of hallucination.
