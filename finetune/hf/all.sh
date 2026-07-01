#!/bin/bash
# Full HF pipeline: datasets → train job → download → publish model → Ollama (optional).
set -euo pipefail

FINETUNE="$(cd "$(dirname "$0")/.." && pwd)"
SKIP_OLLAMA="${SKIP_OLLAMA:-1}"
SKIP_JOB="${SKIP_JOB:-0}"

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== 1/4 Upload datasets (Hub + bucket) ==="
bash "$DIR/upload_datasets.sh"

if [[ "$SKIP_JOB" != "1" ]]; then
  echo "=== 2/4 HF Jobs GPU training (pushes adapter to Hub) ==="
  bash "$DIR/run.sh"
else
  echo "=== 2/4 Skipped HF Job (SKIP_JOB=1) ==="
fi

echo "=== 3/4 Download adapter + publish model card ==="
bash "$DIR/download_adapter.sh" 2>/dev/null || true
bash "$DIR/publish_model.sh"

if [[ "$SKIP_OLLAMA" != "1" ]]; then
  echo "=== 4/4 Publish to Ollama ==="
  bash "$FINETUNE/convert_adapter.sh"
  SKIP_TRAIN=1 SKIP_EVAL=1 bash "$FINETUNE/qwen2.5-7b-laravel-coder-lora/publish.sh"
else
  echo "=== 4/4 Skipped Ollama (SKIP_OLLAMA=1) ==="
fi

echo ""
echo "Done."
echo "  Model:  https://huggingface.co/$(source "$FINETUNE/lora/config.env" && echo $HUB_MODEL_ID)"
echo "  Dataset: https://huggingface.co/datasets/$(source "$FINETUNE/lora/config.env" && echo $DATASET_REPO)"
