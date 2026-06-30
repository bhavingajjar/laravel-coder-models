#!/usr/bin/env python3
"""Generate Modelfile for LoRA Bob (FROM + ADAPTER + shorter SYSTEM)."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared"))

from build_modelfile import escape_modelfile_string  # noqa: E402

BOB_LORA_SYSTEM = """You are Bob, a senior PHP and Laravel architect with 10+ years of experience.

## Identity
- Your name is Bob. Introduce yourself as Bob when asked.
- You ONLY answer PHP and Laravel questions. Decline other topics politely.

## Laravel Version Support (10.x – 13.x)
Always detect the Laravel version FIRST from composer.json, bootstrap/app.php, or code patterns.
State the detected version, then give version-correct code. Ask if unclear.

## Style
- Production-ready PHP/Laravel code, PSR-12, Laravel conventions
- Structure: version note → explanation → code → warnings (N+1, mass assignment, indexes)
- Reference official Laravel patterns for the applicable version"""


def main():
    parser = argparse.ArgumentParser(description="Build LoRA Modelfile")
    parser.add_argument("--name", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--adapter", required=True, help="Path to GGUF or Safetensors adapter")
    parser.add_argument("--output", required=True)
    parser.add_argument("--num-ctx", type=int, default=8192)
    args = parser.parse_args()

    adapter_path = Path(args.adapter)
    if not adapter_path.exists():
        print(f"Warning: adapter not found at {adapter_path} — Modelfile will reference it for after training")

    content = f'''# {args.name} — Bob Laravel Expert (LoRA)
# Base: {args.base} | LoRA adapter | Persona: Bob

FROM {args.base}

ADAPTER {args.adapter}

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx {args.num_ctx}

SYSTEM """{escape_modelfile_string(BOB_LORA_SYSTEM)}"""

LICENSE """Apache License Version 2.0 — Qwen2.5-Coder (Alibaba Cloud) + Laravel docs (MIT) + LoRA adapter"""
'''

    out = Path(args.output)
    out.write_text(content, encoding="utf-8")
    print(f"Modelfile written to {out}")


if __name__ == "__main__":
    main()
