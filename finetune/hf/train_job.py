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
"""LoRA fine-tune on Hugging Face Jobs GPU. Pushes adapter to the Hub when done."""

import json
import os
from pathlib import Path

import torch
from datasets import load_dataset
from huggingface_hub import HfApi
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

BASE_MODEL = os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")
DATASET_REPO = os.environ.get("DATASET_REPO", "bhavin-gajjar/laravel-coder-lora-train")
HUB_MODEL_ID = os.environ.get("HUB_MODEL_ID", "bhavin-gajjar/qwen-laravel-coder")
MAX_SEQ_LENGTH = int(os.environ.get("MAX_SEQ_LENGTH", "1024"))
EPOCHS = int(os.environ.get("EPOCHS", "1"))
LORA_R = int(os.environ.get("LORA_R", "4"))
LORA_ALPHA = int(os.environ.get("LORA_ALPHA", "8"))


def main() -> None:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA required — submit via: bash finetune/hf/run.sh")

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Base model: {BASE_MODEL}")
    print(f"Dataset: {DATASET_REPO} (config: lora_train)")
    print(f"Output hub repo: {HUB_MODEL_ID}")

    api = HfApi()
    api.create_repo(HUB_MODEL_ID, repo_type="model", exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    raw = load_dataset(DATASET_REPO, "lora_train", split="train")

    def to_text(example: dict) -> dict:
        text = tokenizer.apply_chat_template(
            example["messages"], tokenize=False, add_generation_prompt=False
        )
        return {"text": text}

    dataset = raw.map(to_text, remove_columns=raw.column_names)
    print(f"Training samples: {len(dataset)}")

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable()

    model = get_peft_model(
        model,
        LoraConfig(
            r=LORA_R,
            lora_alpha=LORA_ALPHA,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj"],
            bias="none",
            task_type="CAUSAL_LM",
        ),
    )
    model.print_trainable_parameters()

    out_dir = Path("/tmp/qwen-laravel-lora")
    out_dir.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(out_dir / "checkpoints"),
            num_train_epochs=EPOCHS,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            logging_steps=5,
            save_strategy="epoch",
            save_total_limit=1,
            report_to="none",
            bf16=True,
        ),
        train_dataset=dataset,
        processing_class=tokenizer,
        max_seq_length=MAX_SEQ_LENGTH,
    )

    trainer.train()
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)

    print(f"Pushing adapter to {HUB_MODEL_ID}...")
    model.push_to_hub(HUB_MODEL_ID, commit_message="LoRA adapter — Laravel coder Bob")
    tokenizer.push_to_hub(HUB_MODEL_ID)

    meta = {
        "base_model": BASE_MODEL,
        "dataset": DATASET_REPO,
        "dataset_config": "lora_train",
        "epochs": EPOCHS,
        "max_seq_length": MAX_SEQ_LENGTH,
        "lora": {"r": LORA_R, "alpha": LORA_ALPHA, "target_modules": ["q_proj", "v_proj"]},
    }
    api.upload_file(
        path_or_fileobj=json.dumps(meta, indent=2).encode(),
        path_in_repo="training_meta.json",
        repo_id=HUB_MODEL_ID,
        repo_type="model",
    )
    print(f"Done: https://huggingface.co/{HUB_MODEL_ID}")


if __name__ == "__main__":
    main()
