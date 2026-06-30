#!/usr/bin/env python3
"""Minimal CPU LoRA fine-tune for Qwen2.5-Coder-7B (Intel Iris Xe / no CUDA)."""

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
DEFAULT_OUT = ROOT / "qwen2.5-7b-laravel-coder-lora" / "adapters" / "qwen-laravel-lora"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def to_text(example: dict, tokenizer) -> dict:
    messages = example["messages"]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return {"text": text}


def main():
    parser = argparse.ArgumentParser(description="Minimal CPU LoRA for Qwen Laravel Bob")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--train", default=str(DATA_DIR / "laravel_train.jsonl"))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--max-samples", type=int, default=0, help="0 = all")
    parser.add_argument("--max-seq-length", type=int, default=1024)
    args = parser.parse_args()

    train_path = Path(args.train)
    if not train_path.exists():
        raise SystemExit(f"Missing {train_path}. Run: python3 finetune/prepare_dataset.py")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device} (Intel Iris Xe: training uses CPU)")

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    rows = load_jsonl(train_path)
    if args.max_samples > 0:
        rows = rows[: args.max_samples]

    dataset = Dataset.from_list([to_text(r, tokenizer) for r in rows])

    load_kwargs = {"trust_remote_code": True, "torch_dtype": torch.float32}
    if device == "cpu":
        load_kwargs["low_cpu_mem_usage"] = True

    model = AutoModelForCausalLM.from_pretrained(args.model, **load_kwargs)
    model.config.use_cache = False
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    lora_config = LoraConfig(
        r=4,
        lora_alpha=8,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(out_dir / "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=5,
        save_strategy="epoch",
        save_total_limit=1,
        report_to="none",
        use_cpu=(device == "cpu"),
        no_cuda=(device == "cpu"),
        fp16=False,
        bf16=False,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
        max_seq_length=args.max_seq_length,
    )

    print(f"Training on {len(dataset)} samples...")
    trainer.train()
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f"Adapter saved to {out_dir}")


if __name__ == "__main__":
    main()
