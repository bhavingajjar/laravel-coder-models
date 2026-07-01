#!/bin/bash
# Create/update HF model repo — merge LoRA then push full weights.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
PYTHON="${PYTHON:-$VENV/bin/python3}"
ADAPTER="$FINETUNE/$ADAPTER_DIR"

if [[ ! -x "$PYTHON" ]]; then
  echo "Missing venv at $VENV"
  exit 1
fi

if [[ ! -f "$ADAPTER/adapter_config.json" ]]; then
  echo "No adapter at $ADAPTER — train first:"
  echo "  TRAIN_MODE=kaggle bash $FINETUNE/train.sh"
  echo "  TRAIN_MODE=local bash $FINETUNE/local/train.sh"
  exit 1
fi

echo "==> Merge LoRA + push to $HUB_MODEL_ID"
"$PYTHON" "$DIR/merge_and_publish.py"
