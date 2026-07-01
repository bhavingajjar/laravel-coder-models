#!/usr/bin/env python3
"""Local LoRA training — uses CUDA when available, otherwise CPU."""

import argparse
import os
import sys
from pathlib import Path

FINETUNE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FINETUNE))

from lora.train_core import DEFAULT_ADAPTER, DEFAULT_MODEL, DEFAULT_TRAIN, LoraTrainConfig, run_lora_training


def main() -> None:
    parser = argparse.ArgumentParser(description="Local LoRA training (GPU or CPU)")
    parser.add_argument("--model", default=os.environ.get("BASE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--train", default=os.environ.get("TRAIN_FILE", str(DEFAULT_TRAIN)))
    parser.add_argument("--output", default=os.environ.get("ADAPTER_DIR", str(DEFAULT_ADAPTER)))
    parser.add_argument("--epochs", type=int, default=int(os.environ.get("EPOCHS", "1")))
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--max-seq-length", type=int, default=int(os.environ.get("MAX_SEQ_LENGTH", "1024")))
    parser.add_argument("--hub-model-id", default=os.environ.get("HUB_MODEL_ID", ""))
    parser.add_argument("--push-to-hub", action="store_true", help="Upload adapter after training")
    args = parser.parse_args()

    hub_id = args.hub_model_id
    if args.push_to_hub and not hub_id:
        hub_id = os.environ.get("HUB_MODEL_ID", "bhavin-gajjar/qwen-laravel-coder")

    run_lora_training(
        LoraTrainConfig(
            model=args.model,
            train_path=Path(args.train),
            output_dir=Path(args.output),
            epochs=args.epochs,
            max_samples=args.max_samples,
            max_seq_length=args.max_seq_length,
            hub_model_id=hub_id,
        )
    )


if __name__ == "__main__":
    main()
