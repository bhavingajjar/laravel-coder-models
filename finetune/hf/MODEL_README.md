---
license: apache-2.0
language: en
pipeline_tag: text-generation
library_name: transformers
base_model: Qwen/Qwen2.5-Coder-7B-Instruct
tags:
  - laravel
  - php
  - code
  - qwen2.5
  - qwen
  - text-generation
datasets:
  - bhavin-gajjar/laravel-coder-lora-train
---

# Qwen2.5-7B Laravel Coder

**`bhavin-gajjar/qwen-laravel-coder`** — fine-tuned from [Qwen/Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) for Laravel v10–v13 development.

| | |
|---|---|
| Base | Qwen2.5-Coder-7B-Instruct (7B parameters) |
| Dataset | [bhavin-gajjar/laravel-coder-lora-train](https://huggingface.co/datasets/bhavin-gajjar/laravel-coder-lora-train) (`lora_train`, 800 samples) |
| Task | `text-generation` |

## Load (recommended)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL = "bhavin-gajjar/qwen-laravel-coder"
tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
)
```

## Training reference (LoRA — for documentation only)

Training used LoRA on the base model before merging weights into this repo:

| LoRA setting | Value |
|---|---|
| r | 4 |
| alpha | 8 |
| targets | `q_proj`, `v_proj` |
| epochs | 1 |
| samples | 800 |

This repo contains the **merged full model**, not a separate PEFT adapter.

## Ollama

```bash
bash finetune/hf/download_adapter.sh
bash finetune/convert_adapter.sh
SKIP_TRAIN=1 ./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```
