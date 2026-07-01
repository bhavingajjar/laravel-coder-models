#!/usr/bin/env python3
"""Export full laravel_training.jsonl to chat (messages) format for HF / TRL."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "shared" / "data" / "laravel_training.jsonl"
OUT = Path(__file__).resolve().parent / "data" / "laravel_training_chat.jsonl"


def format_chat(item: dict) -> dict:
    user = item["instruction"]
    if item.get("input"):
        user += f"\n\nContext:\n{item['input']}"
    return {
        "messages": [
            {"role": "user", "content": user},
            {"role": "assistant", "content": item["output"]},
        ],
        "version": item.get("version", ""),
        "topic": item.get("topic", ""),
    }


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing {SOURCE}. Run: python3 shared/build_training_data.py")

    OUT.parent.mkdir(exist_ok=True)
    count = 0
    with SOURCE.open(encoding="utf-8") as fin, OUT.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            fout.write(json.dumps(format_chat(json.loads(line)), ensure_ascii=False) + "\n")
            count += 1
    print(f"Wrote {count} items → {OUT}")


if __name__ == "__main__":
    main()
