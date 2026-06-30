#!/bin/bash
# Convert Safetensors LoRA adapter to GGUF for Ollama import (Qwen).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
ADAPTER_DIR="${1:-$DIR/qwen2.5-7b-laravel-coder-lora/adapters/qwen-laravel-lora}"
OUT_GGUF="${2:-$DIR/qwen2.5-7b-laravel-coder-lora/adapters/qwen-laravel-lora.gguf}"
HF_BASE="${HF_BASE:-Qwen/Qwen2.5-Coder-7B-Instruct}"
LLAMA_CPP="${LLAMA_CPP:-$ROOT/../llama.cpp}"

if [[ ! -d "$ADAPTER_DIR" ]]; then
  echo "Adapter dir not found: $ADAPTER_DIR"
  echo "Train first: python3 $DIR/train_lora_minimal.py"
  exit 1
fi

CONVERT="$LLAMA_CPP/convert_lora_to_gguf.py"
if [[ ! -f "$CONVERT" ]]; then
  echo "llama.cpp convert_lora_to_gguf.py not found at $CONVERT"
  echo ""
  echo "Option A — clone llama.cpp next to repo:"
  echo "  git clone https://github.com/ggerganov/llama.cpp $LLAMA_CPP"
  echo ""
  echo "Option B — try Safetensors ADAPTER directly in Modelfile (may work on newer Ollama):"
  echo "  ADAPTER $ADAPTER_DIR"
  echo ""
  echo "Option C — train in Colab, export GGUF adapter, place at:"
  echo "  $OUT_GGUF"
  exit 1
fi

mkdir -p "$(dirname "$OUT_GGUF")"
python3 "$CONVERT" \
  --outfile "$OUT_GGUF" \
  --base "$HF_BASE" \
  --outtype f16 \
  "$ADAPTER_DIR"

echo "GGUF adapter: $OUT_GGUF"
