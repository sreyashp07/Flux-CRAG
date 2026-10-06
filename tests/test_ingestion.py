from backend.ingestion.chunker import split_documents
from backend.ingestion.loader import load_documents


def test_load_documents_reads_only_supported_non_empty_files(tmp_path):
    (tmp_path / "a.md").write_text("# Title\nhello world", encoding="utf-8")
    (tmp_path / "b.txt").write_text("plain text", encoding="utf-8")
    (tmp_path / "c.png").write_bytes(b"\x89PNG")
    (tmp_path / "empty.txt").write_text("   ", encoding="utf-8")

    docs = load_documents(tmp_path)

    assert sorted(d.metadata["source"] for d in docs) == ["a.md", "b.txt"]


def test_split_documents_respects_size_and_keeps_metadata(tmp_path):
    (tmp_path / "long.txt").write_text("word " * 500, encoding="utf-8")
    docs = load_documents(tmp_path)

    chunks = split_documents(docs, chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(len(c.page_content) <= 200 for c in chunks)
    assert all(c.metadata["source"] == "long.txt" for c in chunks)
    assert all("start_index" in c.metadata for c in chunks)
