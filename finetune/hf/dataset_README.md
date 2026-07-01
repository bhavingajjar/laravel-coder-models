---
license: mit
task_categories:
  - text-generation
language:
  - en
tags:
  - laravel
  - php
  - code
  - instruction-tuning
  - laravel-10
  - laravel-11
  - laravel-12
  - laravel-13
size_categories:
  - 1K<n<10K
configs:
  - config_name: raw
    data_files:
      - split: train
        path: raw/laravel_training.jsonl
  - config_name: chat
    data_files:
      - split: train
        path: chat/laravel_training_chat.jsonl
  - config_name: lora_train
    data_files:
      - split: train
        path: lora/laravel_train.jsonl
  - config_name: lora_eval
    data_files:
      - split: train
        path: lora/laravel_eval.jsonl
---

# Laravel Coder LoRA — end-to-end training data

Instruction-tuning datasets for **Laravel Bob** (Qwen / CodeLlama / DeepSeek modelfiles).  
Built from official Laravel docs **v10.x–v13.x** plus version-detection examples.

Each **config** has a single schema — do not mix `raw` (Alpaca) with `chat` / `lora_*` (messages).

## Configs

| Config | Path | Rows | Schema |
|--------|------|------|--------|
| `raw` | `raw/laravel_training.jsonl` | 2019 | `instruction`, `input`, `output`, `topic`, `version` |
| `chat` | `chat/laravel_training_chat.jsonl` | 2019 | `messages`, `topic`, `version` |
| `lora_train` | `lora/laravel_train.jsonl` | 800 | `messages`, `topic`, `version` |
| `lora_eval` | `lora/laravel_eval.jsonl` | 40 | `messages`, `topic`, `version` |

## Auxiliary files (not dataset configs)

| Path | Description |
|------|-------------|
| `few_shot_examples.json` | Modelfile few-shot (JSON array) |
| `laravel_knowledge.md` | RAG / system context digest |
| `meta.json` | Corpus stats |
| `lora/meta.json` | Curated split stats |

## Schema — `raw`

```json
{
  "instruction": "[Laravel 11] Explain routing: Basic Routing",
  "input": "",
  "output": "...",
  "topic": "routing",
  "version": "11.x"
}
```

## Schema — `chat`, `lora_train`, `lora_eval`

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "version": "11.x",
  "topic": "routing"
}
```

## Load in Python

```python
from datasets import load_dataset

raw = load_dataset("bhavin-gajjar/laravel-coder-lora-train", "raw", split="train")
chat = load_dataset("bhavin-gajjar/laravel-coder-lora-train", "chat", split="train")
train = load_dataset("bhavin-gajjar/laravel-coder-lora-train", "lora_train", split="train")
eval_ds = load_dataset("bhavin-gajjar/laravel-coder-lora-train", "lora_eval", split="train")
```

## Regenerate locally

```bash
cd ollama
python3 shared/build_training_data.py
python3 finetune/prepare_dataset.py
python3 finetune/export_chat_dataset.py
bash finetune/upload_dataset_to_hub.sh
```

## Source

Generated from `laravel-docs/{10,11,12,13}.x` via `shared/build_training_data.py`.
