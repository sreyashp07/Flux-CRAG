# ChromaDB Notes

ChromaDB is an open-source vector database designed for storing embeddings and
running similarity search. It can run in memory or in persistent mode, where
data is saved to a local folder on disk.

## Collections

Embeddings are stored in collections. Each record has an ID, an embedding, the
original text and optional metadata. Metadata can be used to filter results at
query time.

## Distance metrics

By default Chroma ranks results by squared L2 distance. Cosine similarity and
inner product can be selected when a collection is created.

## Persistence

Using a persistent client means the index survives restarts, so documents only
need to be embedded once. Re-adding a record with an existing ID updates it
rather than creating a duplicate.
