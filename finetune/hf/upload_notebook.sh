#!/bin/bash
# Upload inference notebook to HF model repo.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
HF="${HF:-$VENV/bin/hf}"

if [[ -z "${HF_TOKEN:-}" && -f "$HOME/.cache/huggingface/token" ]]; then
  export HF_TOKEN="$(cat "$HOME/.cache/huggingface/token")"
fi

echo "==> Upload inference notebook to $HUB_MODEL_ID"
"$HF" upload "$HUB_MODEL_ID" "$DIR/qwen-laravel-coder.ipynb" . --repo-type model \
  --commit-message "Add Colab inference notebook (explicit model load)"

echo "https://huggingface.co/$HUB_MODEL_ID/blob/main/qwen-laravel-coder.ipynb"
