# Hugging Face Jobs LoRA training

Train on **HF managed GPU** when local CUDA is not available.  
Requires **HF Pro** + **prepaid credits** (~$1–2 per run on `a10g-small`).

```bash
export HF_TOKEN="hf_..."   # or: hf auth login
bash finetune/hf/run.sh
```

## Workflow

1. `upload_datasets.sh` — rebuild + push datasets to Hub + bucket
2. `run.sh` — submit GPU job (`train_job.py`)
3. `download_adapter.sh` — pull adapter to local `ADAPTER_DIR`
4. `convert_adapter.sh` + `publish.sh` — ship to Ollama

```bash
bash finetune/hf/download_adapter.sh
bash finetune/convert_adapter.sh
SKIP_TRAIN=1 SKIP_EVAL=1 ./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```

## Hub targets

| Resource | ID |
|----------|-----|
| Dataset | `bhavin-gajjar/laravel-coder-lora-train` |
| Adapter model (merged) | `bhavin-gajjar/qwen-laravel-coder` |
| Bucket | `bhavin-gajjar/mybucket/laravel-coder-lora-train` |

## Options

| Env var | Default |
|---------|---------|
| `HF_FLAVOR` | `a10g-small` |
| `HF_TIMEOUT` | `2h` |

Config shared with local training: `finetune/lora/config.env`
