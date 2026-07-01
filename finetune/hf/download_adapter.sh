#!/bin/bash
# Pull trained LoRA adapter from Hugging Face Hub into local Ollama publish path.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
HF="${HF:-$VENV/bin/hf}"
OUT="$FINETUNE/$ADAPTER_DIR"

mkdir -p "$OUT"
"$HF" download "$HUB_MODEL_ID" --local-dir "$OUT" --exclude "training_meta.json"
echo "Adapter saved to $OUT"
