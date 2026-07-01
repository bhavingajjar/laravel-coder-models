"""Merge LoRA adapter into base model and publish."""

from __future__ import annotations

import json
import os
from pathlib import Path

import torch
from huggingface_hub import HfApi
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

FINETUNE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ADAPTER = FINETUNE_ROOT / "qwen2.5-7b-laravel-coder-lora" / "adapters" / "qwen-laravel-lora"
DEFAULT_MERGED = FINETUNE_ROOT / "qwen2.5-7b-laravel-coder-lora" / "merged" / "qwen-laravel-coder"


def merge_lora_adapter(
    adapter_dir: Path,
    output_dir: Path,
    base_model: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
) -> Path:
    if not (adapter_dir / "adapter_config.json").exists():
        raise SystemExit(f"Missing adapter at {adapter_dir}")

    use_gpu = torch.cuda.is_available()
    dtype = torch.bfloat16 if use_gpu else torch.float16
    print(f"Merging LoRA into base ({'GPU' if use_gpu else 'CPU'})...")

    tokenizer = AutoTokenizer.from_pretrained(str(adapter_dir), trust_remote_code=True)
    load_kwargs: dict = {"trust_remote_code": True, "torch_dtype": dtype, "low_cpu_mem_usage": True}
    if use_gpu:
        load_kwargs["device_map"] = "auto"
    else:
        load_kwargs["device_map"] = {"": "cpu"}

    base = AutoModelForCausalLM.from_pretrained(base_model, **load_kwargs)
    model = PeftModel.from_pretrained(base, str(adapter_dir))
    merged = model.merge_and_unload()

    output_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Merged model saved to {output_dir}")
    return output_dir


def push_merged_to_hub(
    merged_dir: Path,
    hub_model_id: str,
    readme_path: Path | None = None,
) -> None:
    api = HfApi()
    api.create_repo(hub_model_id, repo_type="model", exist_ok=True)

    if readme_path and readme_path.exists():
        api.upload_file(
            path_or_fileobj=str(readme_path),
            path_in_repo="README.md",
            repo_id=hub_model_id,
            repo_type="model",
        )

    print(f"Pushing merged model to {hub_model_id} (this may take a while)...")
    api.upload_folder(
        folder_path=str(merged_dir),
        repo_id=hub_model_id,
        repo_type="model",
        commit_message="Qwen2.5-7B Laravel Coder — merged fine-tuned weights",
    )
    print(f"Published: https://huggingface.co/{hub_model_id}")
