"""Shared LoRA training logic for local and Hugging Face Jobs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import torch
from datasets import Dataset
from huggingface_hub import HfApi
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

FINETUNE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
DEFAULT_ADAPTER = FINETUNE_ROOT / "qwen2.5-7b-laravel-coder-lora" / "adapters" / "qwen-laravel-lora"
DEFAULT_TRAIN = FINETUNE_ROOT / "data" / "laravel_train.jsonl"


@dataclass
class LoraTrainConfig:
    model: str = DEFAULT_MODEL
    train_path: Path = DEFAULT_TRAIN
    output_dir: Path = DEFAULT_ADAPTER
    epochs: int = 1
    max_samples: int = 0
    max_seq_length: int = 1024
    lora_r: int = 4
    lora_alpha: int = 8
    hub_model_id: str = ""
    require_cuda: bool = False


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def messages_to_text(example: dict, tokenizer) -> dict:
    text = tokenizer.apply_chat_template(
        example["messages"], tokenize=False, add_generation_prompt=False
    )
    return {"text": text}


def build_dataset(rows: list[dict], tokenizer) -> Dataset:
    return Dataset.from_list([messages_to_text(r, tokenizer) for r in rows])


def resolve_device(require_cuda: bool = False) -> str:
    if torch.cuda.is_available():
        return "cuda"
    if require_cuda:
        raise SystemExit("CUDA required. Use HF Jobs: bash finetune/hf/run.sh")
    return "cpu"


def run_lora_training(cfg: LoraTrainConfig) -> Path:
    train_path = Path(cfg.train_path)
    if not train_path.exists():
        raise SystemExit(f"Missing {train_path}. Run: python3 finetune/prepare_dataset.py")

    device = resolve_device(cfg.require_cuda)
    use_gpu = device == "cuda"
    print(f"Device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if use_gpu else ""))

    tokenizer = AutoTokenizer.from_pretrained(cfg.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    rows = load_jsonl(train_path)
    if cfg.max_samples > 0:
        rows = rows[: cfg.max_samples]

    dataset = build_dataset(rows, tokenizer)

    seq_len = cfg.max_seq_length
    load_kwargs: dict = {"trust_remote_code": True, "low_cpu_mem_usage": True}
    if use_gpu:
        load_kwargs["torch_dtype"] = torch.bfloat16
        load_kwargs["device_map"] = "auto"
    else:
        # 7B fp32 needs ~28GB RAM; fp16 + disk offload fits ~16GB machines
        load_kwargs["torch_dtype"] = torch.float16
        offload = Path(cfg.output_dir).parent / "offload"
        offload.mkdir(parents=True, exist_ok=True)
        load_kwargs["device_map"] = "auto"
        load_kwargs["offload_folder"] = str(offload)
        load_kwargs["offload_state_dict"] = True
        if seq_len > 512:
            seq_len = 512
            print("CPU mode: reduced max_seq_length to 512 for memory")

    model = AutoModelForCausalLM.from_pretrained(cfg.model, **load_kwargs)
    model.config.use_cache = False
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    model = get_peft_model(
        model,
        LoraConfig(
            r=cfg.lora_r,
            lora_alpha=cfg.lora_alpha,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj"],
            bias="none",
            task_type="CAUSAL_LM",
        ),
    )
    model.print_trainable_parameters()

    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(out_dir / "checkpoints"),
            num_train_epochs=cfg.epochs,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            logging_steps=5,
            save_strategy="epoch",
            save_total_limit=1,
            report_to="none",
            use_cpu=not use_gpu,
            no_cuda=not use_gpu,
            bf16=use_gpu,
            fp16=False,
        ),
        train_dataset=dataset,
        processing_class=tokenizer,
        max_seq_length=seq_len,
    )

    print(f"Training on {len(dataset)} samples...")
    trainer.train()
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f"Adapter saved to {out_dir}")

    if cfg.hub_model_id and os.environ.get("PUSH_ADAPTER_TO_HUB", "0") == "1":
        push_adapter_to_hub(model, tokenizer, cfg)

    return out_dir


def push_adapter_to_hub(model, tokenizer, cfg: LoraTrainConfig) -> None:
    api = HfApi()
    api.create_repo(cfg.hub_model_id, repo_type="model", exist_ok=True)
    print(f"Pushing adapter to {cfg.hub_model_id}...")
    model.push_to_hub(cfg.hub_model_id, commit_message="LoRA adapter — Laravel coder Bob")
    tokenizer.push_to_hub(cfg.hub_model_id)
    meta = {
        "base_model": cfg.model,
        "epochs": cfg.epochs,
        "max_seq_length": cfg.max_seq_length,
        "lora": {"r": cfg.lora_r, "alpha": cfg.lora_alpha, "target_modules": ["q_proj", "v_proj"]},
    }
    api.upload_file(
        path_or_fileobj=json.dumps(meta, indent=2).encode(),
        path_in_repo="training_meta.json",
        repo_id=cfg.hub_model_id,
        repo_type="model",
    )
    print(f"Hub: https://huggingface.co/{cfg.hub_model_id}")
