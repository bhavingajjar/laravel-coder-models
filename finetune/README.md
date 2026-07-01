# finetune/ — Experimental LoRA Bob

Optional accuracy upgrade via LoRA fine-tuning. **If this fails, use `../modelfile/` — production is unchanged.**

## Layout

```
finetune/
├── train.sh           # auto: local CUDA → kaggle → hf → local CPU
├── lora/config.env    # shared model + Hub + Kaggle settings
├── local/             # train on this machine (GPU or CPU)
├── hf/                # HF Jobs GPU, merge + publish
├── kaggle/            # Kaggle dataset, GPU kernel, weights publish
└── data/              # generated JSONL splits
```

## Quick start

```bash
cd /var/www/html/ollama
pip install -r finetune/requirements.txt

# Auto-pick: local CUDA → Kaggle GPU → HF Jobs → local CPU
bash finetune/train.sh

# Or force one path:
TRAIN_MODE=local bash finetune/train.sh
TRAIN_MODE=kaggle bash finetune/train.sh
TRAIN_MODE=hf bash finetune/train.sh
```

## Publish to Ollama

```bash
bash finetune/hf/download_adapter.sh   # only if trained on HF
bash finetune/convert_adapter.sh
SKIP_TRAIN=1 ./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```

| Model | URL |
|-------|-----|
| Production (modelfile/) | https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder |
| LoRA (finetune/) | https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder-lora |

## Hub resources

| Resource | ID |
|----------|-----|
| Dataset | [bhavin-gajjar/laravel-coder-lora-train](https://huggingface.co/datasets/bhavin-gajjar/laravel-coder-lora-train) |
| Model (merged) | [bhavin-gajjar/qwen-laravel-coder](https://huggingface.co/bhavin-gajjar/qwen-laravel-coder) |
| Bucket | [bhavin-gajjar/mybucket/laravel-coder-lora-train](https://huggingface.co/buckets/bhavin-gajjar/mybucket/laravel-coder-lora-train) |

Upload datasets only: `bash finetune/hf/upload_datasets.sh`

## Settings

Edit `finetune/lora/config.env` for `BASE_MODEL`, `HUB_MODEL_ID`, `HF_FLAVOR`, etc.

## Files

| Path | Purpose |
|------|---------|
| `local/train.sh` | Local GPU/CPU training |
| `hf/run.sh` | HF Jobs GPU training |
| `hf/upload_datasets.sh` | Push datasets to Hub + bucket |
| `hf/download_adapter.sh` | Pull adapter from Hub |
| `prepare_dataset.py` | Curate train/eval JSONL |
| `convert_adapter.sh` | Safetensors → GGUF |
| `evaluate.py` | A/B modelfile vs LoRA |
