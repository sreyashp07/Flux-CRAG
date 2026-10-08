"""CLI: ask a question and watch the agent's decisions stream live.

Usage (from the repo root):
    python -m scripts.ask "How do conditional edges work in LangGraph?"
"""
import argparse
import sys

from backend.runner import stream_run


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Ask Flux-CRAG a question.")
    parser.add_argument("question", nargs="+", help="The question to ask")
    args = parser.parse_args()
    question = " ".join(args.question)

    streaming_tokens = False
    for item in stream_run(question):
        kind = item["type"]

        if kind == "run_started":
            print(f"\n[run {item['run_id']}] {item['question']}\n")

        elif kind == "event":
            token = item["data"].get("token")
            if item["status"] == "progress" and token is not None:
                print(token, end="", flush=True)
                streaming_tokens = True
                continue
            if streaming_tokens:
                print()
                streaming_tokens = False
            print(f"[{item['node']:<15}] {item['status']:<9} {item['message']}")

        elif kind == "error":
            print(f"\n[error] {item['message']}")
            return 1

        elif kind == "final":
            print("\n" + "-" * 60)
            print("PATH   :", " -> ".join(item["path"]))
            print("WEB    :", "yes" if item["used_web_search"] else "no")
            for source in item["sources"]:
                print(f"SOURCE : [{source['id']}] ({source['origin']}) {source['location']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
