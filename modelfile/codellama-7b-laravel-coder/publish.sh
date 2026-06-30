#!/bin/bash
# Publish codellama-7b-laravel-coder (Bob)
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
MODEL_NAME="codellama-7b-laravel-coder"
BASE_MODEL="${1:-codellama:7b}"
OLLAMA_USER="${OLLAMA_USER:-bhavingajjar}"

python3 "$ROOT/shared/build_training_data.py"
python3 "$ROOT/shared/build_modelfile.py" \
  --name "$MODEL_NAME" \
  --base "$BASE_MODEL" \
  --output "$DIR/Modelfile" \
  --num-ctx 8192 \
  --license "Llama 2 Community License — Code Llama (Meta) + Laravel docs (MIT)"

ollama create "$MODEL_NAME" -f "$DIR/Modelfile"
ollama cp "$MODEL_NAME" "${OLLAMA_USER}/${MODEL_NAME}"
ollama push "${OLLAMA_USER}/${MODEL_NAME}"

echo "Published: https://ollama.com/${OLLAMA_USER}/${MODEL_NAME}"
