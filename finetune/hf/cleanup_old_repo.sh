#!/bin/bash
# Delete old HF model repo after successful publish to qwen-laravel-coder.
set -euo pipefail

FINETUNE="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
HF="${HF:-$VENV/bin/hf}"
ADAPTER="$FINETUNE/$ADAPTER_DIR"
MERGED="$FINETUNE/qwen2.5-7b-laravel-coder-lora/merged/qwen-laravel-coder"

if [[ -z "${HF_TOKEN:-}" && -f "$HOME/.cache/huggingface/token" ]]; then
  export HF_TOKEN="$(cat "$HOME/.cache/huggingface/token")"
fi

if [[ ! -f "$ADAPTER/adapter_config.json" && ! -d "$MERGED" ]]; then
  echo "No trained adapter or merged model — train first."
  exit 1
fi

echo "==> Delete old repo: $HUB_MODEL_ID_OLD"
"$HF" repo delete "$HUB_MODEL_ID_OLD" --repo-type model --yes || echo "Old repo already removed or not found"

echo "Done. New model: https://huggingface.co/$HUB_MODEL_ID"
