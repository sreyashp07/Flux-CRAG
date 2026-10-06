"""CLI: load -> chunk -> embed -> index documents into the local ChromaDB store.

Usage (from the repo root):
    python -m scripts.ingest [--docs-dir PATH] [--reset]
"""
import argparse
from pathlib import Path

from backend.config import get_settings
from backend.ingestion.chunker import split_documents
from backend.ingestion.indexer import collection_count, index_documents
from backend.ingestion.loader import load_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into Flux-CRAG.")
    parser.add_argument("--docs-dir", type=Path, default=None, help="Folder of .txt/.md files")
    parser.add_argument("--reset", action="store_true", help="Wipe the collection first")
    args = parser.parse_args()

    settings = get_settings()
    docs_dir = args.docs_dir or settings.docs_dir

    documents = load_documents(docs_dir)
    print(f"[ingest] Loaded {len(documents)} document(s) from {docs_dir}")
    if not documents:
        print("[ingest] Nothing to index. Add .txt or .md files and retry.")
        return

    chunks = split_documents(documents)
    print(f"[ingest] Split into {len(chunks)} chunk(s) "
          f"(size={settings.chunk_size}, overlap={settings.chunk_overlap})")

    indexed = index_documents(chunks, reset=args.reset)
    print(f"[ingest] Indexed {indexed} unique chunk(s) into '{settings.collection_name}'")
    print(f"[ingest] Collection now holds {collection_count()} chunk(s)")


if __name__ == "__main__":
    main()
