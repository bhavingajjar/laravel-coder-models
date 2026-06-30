#!/usr/bin/env python3
"""Compare modelfile Bob vs LoRA Bob on eval prompts via Ollama API."""

import argparse
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_HOST = "http://127.0.0.1:11434"


def ollama_chat(model: str, user: str, host: str) -> str:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": user}],
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return data.get("message", {}).get("content", "")


def score_response(text: str, expected_version: str = "") -> int:
    s = 0
    lower = text.lower()
    if "laravel" in lower:
        s += 1
    if "```" in text or "<?php" in text:
        s += 2
    if expected_version and expected_version.replace(".x", "") in lower:
        s += 2
    if "detected" in lower and "laravel" in lower:
        s += 2
    if len(text) > 100:
        s += 1
    return s


def main():
    parser = argparse.ArgumentParser(description="A/B eval: modelfile vs LoRA Bob")
    parser.add_argument("--modelfile-model", default="qwen2.5-7b-laravel-coder")
    parser.add_argument("--lora-model", default="qwen2.5-7b-laravel-coder-lora")
    parser.add_argument("--eval", default=str(DATA_DIR / "laravel_eval.jsonl"))
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--max-prompts", type=int, default=10)
    args = parser.parse_args()

    eval_path = Path(args.eval)
    if not eval_path.exists():
        raise SystemExit(f"Missing {eval_path}. Run prepare_dataset.py first.")

    rows = []
    with eval_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    rows = rows[: args.max_prompts]

    mf_score = lora_score = 0
    results = []

    for row in rows:
        user = row["messages"][0]["content"]
        version = row.get("version", "")
        try:
            mf = ollama_chat(args.modelfile_model, user, args.host)
            lr = ollama_chat(args.lora_model, user, args.host)
        except Exception as e:
            print(f"Ollama error (is ollama running?): {e}")
            return 1

        ms = score_response(mf, version)
        ls = score_response(lr, version)
        mf_score += ms
        lora_score += ls
        results.append({"user": user[:80], "modelfile": ms, "lora": ls})

    print(json.dumps({
        "modelfile_model": args.modelfile_model,
        "lora_model": args.lora_model,
        "modelfile_score": mf_score,
        "lora_score": lora_score,
        "lora_wins": lora_score > mf_score,
        "prompts": len(rows),
        "details": results,
    }, indent=2))

    if lora_score > mf_score:
        print("\n✓ LoRA beats modelfile — safe to publish -lora tag")
        return 0
    print("\n✗ LoRA did not beat modelfile — do NOT push -lora tag")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
