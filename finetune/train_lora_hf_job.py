# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "torch",
#   "transformers>=4.44.0",
#   "datasets>=2.18.0",
#   "peft>=0.11.0",
#   "trl>=0.9.0",
#   "accelerate>=0.30.0",
#   "sentencepiece>=0.2.0",
#   "huggingface_hub",
# ]
# ///
"""Backward-compat — delegates to finetune/hf/train_job.py (HF Jobs uv script)."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "hf" / "train_job.py"), run_name="__main__")
