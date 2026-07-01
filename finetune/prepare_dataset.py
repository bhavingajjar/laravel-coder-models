#!/usr/bin/env python3
"""Curate laravel_training.jsonl into a small high-quality train/eval set for minimal LoRA."""

import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "shared" / "data" / "laravel_training.jsonl"
OUT_DIR = Path(__file__).resolve().parent / "data"
OUT_DIR.mkdir(exist_ok=True)

MAX_TRAIN = 800
MAX_EVAL = 40
MIN_OUTPUT_LEN = 120

ANCHOR_ONLY = re.compile(r"^<a name=", re.MULTILINE)


def quality_score(item: dict) -> int:
    output = item.get("output", "")
    if len(output) < MIN_OUTPUT_LEN:
        return 0
    if ANCHOR_ONLY.match(output.strip()) and "```" not in output:
        return 0

    score = 1
    if "```" in output or "<?php" in output:
        score += 4
    if "artisan" in output.lower():
        score += 2
    if "Detected Laravel" in output:
        score += 6
    if item.get("version"):
        score += 1
    if item.get("input"):
        score += 2
    if "laravel" in output.lower()[:200]:
        score += 1
    # Penalize TOC-only bullet dumps
    bullets = output[:600].count("\n- ")
    if bullets > 12 and "```" not in output:
        score -= 3
    return max(score, 0)


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


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Run shared/build_training_data.py first. Missing {SOURCE}")

    items = []
    with SOURCE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    scored = [(quality_score(i), i) for i in items]
    scored = [(s, i) for s, i in scored if s >= 2]
    scored.sort(key=lambda x: -x[0])

    random.seed(42)
    priority = [i for s, i in scored if s >= 6]
    pool = [i for s, i in scored if i not in priority]
    random.shuffle(pool)

    eval_items = pool[:MAX_EVAL]
    train_pool = priority + [i for i in pool if i not in eval_items]
    train_items = train_pool[:MAX_TRAIN]

    for name, subset in [("laravel_train.jsonl", train_items), ("laravel_eval.jsonl", eval_items)]:
        path = OUT_DIR / name
        with path.open("w", encoding="utf-8") as f:
            for item in subset:
                f.write(json.dumps(format_chat(item), ensure_ascii=False) + "\n")
        print(f"Wrote {len(subset)} items → {path}")

    meta = {
        "source": str(SOURCE),
        "train_count": len(train_items),
        "eval_count": len(eval_items),
        "priority_version_detection": len(priority),
        "scored_pairs": len(scored),
    }
    (OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
