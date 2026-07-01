#!/bin/bash
# Train LoRA on Hugging Face Jobs GPU. Requires HF Pro + prepaid credits.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
ROOT="$(cd "$FINETUNE/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
HF="${HF:-$VENV/bin/hf}"

if [[ -z "${HF_TOKEN:-}" && -f "$HOME/.cache/huggingface/token" ]]; then
  export HF_TOKEN="$(cat "$HOME/.cache/huggingface/token")"
fi
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "Set HF_TOKEN or run: hf auth login"
  exit 1
fi

echo "==> Rebuild + upload datasets"
bash "$DIR/upload_datasets.sh"

echo "==> Submit HF Job (GPU: $HF_FLAVOR, timeout: $HF_TIMEOUT)"
echo "    Watch: https://huggingface.co/jobs"
"$HF" jobs uv run \
  --flavor "$HF_FLAVOR" \
  --timeout "$HF_TIMEOUT" \
  --secrets HF_TOKEN \
  --env "BASE_MODEL=$BASE_MODEL" \
  --env "DATASET_REPO=$DATASET_REPO" \
  --env "HUB_MODEL_ID=$HUB_MODEL_ID" \
  --env "EPOCHS=$EPOCHS" \
  --env "MAX_SEQ_LENGTH=$MAX_SEQ_LENGTH" \
  --env "LORA_R=$LORA_R" \
  --env "LORA_ALPHA=$LORA_ALPHA" \
  "$DIR/train_job.py"

echo ""
echo "When the job finishes:"
echo "  bash $DIR/download_adapter.sh"
echo "  bash $DIR/publish_model.sh"
echo "  SKIP_TRAIN=1 SKIP_EVAL=1 $FINETUNE/qwen2.5-7b-laravel-coder-lora/publish.sh"
