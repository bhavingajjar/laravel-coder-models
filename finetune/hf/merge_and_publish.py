#!/usr/bin/env python3
"""Merge local LoRA adapter and push full model to Hugging Face Hub."""

import os
import sys
from pathlib import Path

FINETUNE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FINETUNE))

from lora.merge_core import DEFAULT_ADAPTER, DEFAULT_MERGED, merge_lora_adapter, push_merged_to_hub

README = Path(__file__).resolve().parent / "MODEL_README.md"


def main() -> None:
    base = os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")
    hub_id = os.environ.get("HUB_MODEL_ID", "bhavin-gajjar/qwen-laravel-coder")
    adapter = Path(os.environ.get("ADAPTER_DIR", str(DEFAULT_ADAPTER)))
    if not adapter.is_absolute():
        adapter = FINETUNE / adapter
    merged = Path(os.environ.get("MERGED_DIR", str(DEFAULT_MERGED)))
    if not merged.is_absolute():
        merged = FINETUNE / merged

    merge_lora_adapter(adapter, merged, base_model=base)
    push_merged_to_hub(merged, hub_id, readme_path=README)


if __name__ == "__main__":
    main()
