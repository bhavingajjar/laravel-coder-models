# LoRA training layout

```
finetune/
├── train.sh              # entry: auto-pick local vs HF
├── lora/
│   ├── config.env        # shared settings (model, paths, Hub IDs)
│   └── train_core.py     # shared training logic
├── local/                # train on this machine (CUDA or CPU)
│   ├── train.sh
│   └── train.py
├── hf/                   # train on Hugging Face Jobs GPU
│   ├── run.sh
│   ├── train_job.py
│   ├── upload_datasets.sh
│   └── download_adapter.sh
└── data/                 # generated train/eval JSONL (both paths use this)
```

## Quick start

```bash
cd /var/www/html/ollama
pip install -r finetune/requirements.txt

# Auto: local GPU if CUDA, else HF Jobs
bash finetune/train.sh

# Force local (GPU or CPU)
TRAIN_MODE=local bash finetune/train.sh

# Force Hugging Face Jobs GPU
TRAIN_MODE=hf bash finetune/train.sh
```

## After training

```bash
# If trained on HF, download adapter first:
bash finetune/hf/download_adapter.sh

bash finetune/convert_adapter.sh
SKIP_TRAIN=1 ./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```

See `local/README.md` and `hf/README.md` for details.
