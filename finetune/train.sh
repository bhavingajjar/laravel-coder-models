#!/bin/bash
# LoRA training entry point — local, Kaggle GPU, or HF Jobs.
#
# Usage:
#   bash finetune/train.sh
#   TRAIN_MODE=local|kaggle|hf bash finetune/train.sh
set -euo pipefail

FINETUNE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

MODE="${TRAIN_MODE:-auto}"

has_cuda() {
  "$FINETUNE/${VENV_DIR}/bin/python3" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)" 2>/dev/null
}

has_kaggle_token() {
  [[ -n "${KAGGLE_API_TOKEN:-}" ]] || [[ -f "$HOME/.kaggle/kaggle.json" ]]
}

if [[ "$MODE" == "auto" ]]; then
  if has_cuda; then
    MODE="local"
  elif has_kaggle_token; then
    MODE="kaggle"
  elif [[ -n "${HF_TOKEN:-}" ]] || command -v hf &>/dev/null; then
    MODE="hf"
  else
    MODE="local"
    echo "No CUDA/Kaggle/HF — falling back to local CPU (slow)"
  fi
fi

case "$MODE" in
  local)
    echo "==> TRAIN_MODE=local"
    exec bash "$FINETUNE/local/train.sh"
    ;;
  kaggle)
    echo "==> TRAIN_MODE=kaggle (GPU kernel — recommended when local OOM)"
    exec bash "$FINETUNE/kaggle/all.sh"
    ;;
  hf)
    echo "==> TRAIN_MODE=hf (Hugging Face Jobs)"
    exec bash "$FINETUNE/hf/run.sh"
    ;;
  *)
    echo "Unknown TRAIN_MODE=$MODE (use: auto, local, kaggle, hf)"
    exit 1
    ;;
esac
