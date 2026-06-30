#!/bin/bash
# Publish qwen2.5-7b-laravel-coder-lora (Bob + LoRA adapter)
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
MODEL_NAME="qwen2.5-7b-laravel-coder-lora"
BASE_MODEL="${1:-qwen2.5-coder:latest}"
OLLAMA_USER="${OLLAMA_USER:-bhavingajjar}"
ADAPTER_GGUF="$DIR/adapters/qwen-laravel-lora.gguf"
ADAPTER_SAFE="$DIR/adapters/qwen-laravel-lora"
SKIP_EVAL="${SKIP_EVAL:-0}"
SKIP_TRAIN="${SKIP_TRAIN:-1}"

# Rebuild shared training data
python3 "$ROOT/shared/build_training_data.py"
python3 "$FINETUNE/prepare_dataset.py"

if [[ "$SKIP_TRAIN" != "1" ]]; then
  python3 "$FINETUNE/train_lora_minimal.py"
  if [[ -f "$FINETUNE/convert_adapter.sh" ]]; then
    bash "$FINETUNE/convert_adapter.sh" "$ADAPTER_SAFE" "$ADAPTER_GGUF" || true
  fi
fi

# Prefer GGUF adapter; fall back to Safetensors directory
ADAPTER_PATH="$ADAPTER_GGUF"
if [[ ! -f "$ADAPTER_GGUF" && -d "$ADAPTER_SAFE" ]]; then
  echo "GGUF not found — using Safetensors adapter dir (Ollama may accept on recent versions)"
  ADAPTER_PATH="$ADAPTER_SAFE"
fi

if [[ ! -f "$ADAPTER_GGUF" && ! -d "$ADAPTER_SAFE" ]]; then
  echo "No adapter found. Train first:"
  echo "  pip install -r $FINETUNE/requirements.txt"
  echo "  SKIP_TRAIN=0 $0"
  echo "Or place adapter at $ADAPTER_GGUF"
  exit 1
fi

python3 "$FINETUNE/build_lora_modelfile.py" \
  --name "$MODEL_NAME" \
  --base "$BASE_MODEL" \
  --adapter "$ADAPTER_PATH" \
  --output "$DIR/Modelfile"

ollama create "$MODEL_NAME" -f "$DIR/Modelfile"

if [[ "$SKIP_EVAL" != "1" ]]; then
  python3 "$FINETUNE/evaluate.py" \
    --modelfile-model "qwen2.5-7b-laravel-coder" \
    --lora-model "$MODEL_NAME" || {
    echo "Eval: LoRA did not beat modelfile. Skipping push (modelfile/ production unchanged)."
    echo "Force push with: SKIP_EVAL=1 $0"
    exit 2
  }
fi

ollama cp "$MODEL_NAME" "${OLLAMA_USER}/${MODEL_NAME}"
ollama push "${OLLAMA_USER}/${MODEL_NAME}"

echo "Published: https://ollama.com/${OLLAMA_USER}/${MODEL_NAME}"
