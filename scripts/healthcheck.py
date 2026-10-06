"""Verify the local stack: Ollama reachable, models pulled, ChromaDB populated, LLM responding.

Usage (from the repo root):
    python -m scripts.healthcheck
"""
import json
import sys
import urllib.error
import urllib.request

from backend.config import get_settings


def _installed_models(base_url: str) -> list[str]:
    with urllib.request.urlopen(f"{base_url}/api/tags", timeout=5) as resp:
        payload = json.load(resp)
    return [m["name"] for m in payload.get("models", [])]


def _has_model(installed: list[str], wanted: str) -> bool:
    candidates = {wanted} if ":" in wanted else {wanted, f"{wanted}:latest"}
    return any(name in candidates for name in installed)


def main() -> int:
    settings = get_settings()
    ok = True

    print(f"[check] Ollama at {settings.ollama_base_url}")
    try:
        installed = _installed_models(settings.ollama_base_url)
    except (urllib.error.URLError, OSError) as exc:
        print(f"  [FAIL] Cannot reach Ollama: {exc}")
        print("         Start the Ollama app (or run: ollama serve) and retry.")
        return 1
    print("  [ OK ] Ollama is reachable")

    for label, model in (("LLM", settings.llm_model), ("Embedding", settings.embedding_model)):
        if _has_model(installed, model):
            print(f"  [ OK ] {label} model '{model}' is installed")
        else:
            print(f"  [FAIL] {label} model '{model}' is missing -> run: ollama pull {model}")
            ok = False

    print(f"[check] ChromaDB at {settings.chroma_dir}")
    from backend.ingestion.indexer import collection_count

    count = collection_count()
    if count > 0:
        print(f"  [ OK ] Collection '{settings.collection_name}' holds {count} chunk(s)")
    else:
        print("  [FAIL] Collection is empty -> run: python -m scripts.ingest --reset")
        ok = False

    if _has_model(installed, settings.llm_model):
        print("[check] Pinging the LLM (first call can take a while to load the model)...")
        from backend.llm import get_llm

        reply = get_llm().invoke("Reply with the single word: ready")
        print(f"  [ OK ] LLM replied: {str(reply.content).strip()[:60]}")

    print("[check] All good." if ok else "[check] Fix the items marked FAIL above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
