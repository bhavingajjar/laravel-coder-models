#!/bin/bash
# Full local pipeline: train → push HF → convert → publish Ollama.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

PUSH_TO_HUB="${PUSH_TO_HUB:-1}"
SKIP_EVAL="${SKIP_EVAL:-1}"
ADAPTER="$FINETUNE/$ADAPTER_DIR"

echo "=== 1/4 Local LoRA training ==="
PUSH_TO_HUB="$PUSH_TO_HUB" bash "$DIR/train.sh"

if [[ ! -f "$ADAPTER/adapter_config.json" ]]; then
  echo "Training failed — no adapter at $ADAPTER"
  exit 1
fi

echo "=== 2/4 Merge + push merged model to Hugging Face ==="
bash "$FINETUNE/hf/publish_model.sh"

echo "=== 2b/4 Publish Kaggle weights (optional) ==="
if [[ -n "${KAGGLE_API_TOKEN:-}" ]] || [[ -f "$HOME/.kaggle/kaggle.json" ]]; then
  bash "$FINETUNE/kaggle/publish_model.sh" || echo "Kaggle publish skipped"
fi

echo "=== 3/4 Convert adapter to GGUF (optional) ==="
bash "$FINETUNE/convert_adapter.sh" "$ADAPTER" "$FINETUNE/qwen2.5-7b-laravel-coder-lora/adapters/qwen-laravel-lora.gguf" || {
  echo "GGUF convert skipped — Ollama will use Safetensors adapter"
}

echo "=== 4/4 Publish to Ollama ==="
SKIP_TRAIN=1 SKIP_EVAL="$SKIP_EVAL" bash "$FINETUNE/qwen2.5-7b-laravel-coder-lora/publish.sh"

echo ""
echo "Done."
echo "  HF:     https://huggingface.co/$HUB_MODEL_ID"
echo "  Ollama: https://ollama.com/${OLLAMA_USER:-bhavingajjar}/qwen2.5-7b-laravel-coder-lora"
