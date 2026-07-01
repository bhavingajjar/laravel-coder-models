#!/bin/bash
# Wait for in-flight local training, then HF + Ollama publish.
set -euo pipefail

FINETUNE="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"
ADAPTER="$FINETUNE/$ADAPTER_DIR"
LOG="$FINETUNE/train.log"
POLL="${POLL_SECS:-60}"

echo "Waiting for adapter at $ADAPTER/adapter_config.json ..."
echo "Monitor: tail -f $LOG"

while [[ ! -f "$ADAPTER/adapter_config.json" ]]; do
  if ! pgrep -f "finetune/local/train.py" >/dev/null 2>&1; then
    if grep -q "Adapter saved to\|Hub: https://" "$LOG" 2>/dev/null; then
      break
    fi
    if grep -qi "Error\|Traceback\|SystemExit" "$LOG" 2>/dev/null; then
      echo "Training appears failed. Check $LOG"
      exit 1
    fi
    echo "$(date -Iseconds) — training process not running, still waiting for adapter..."
  fi
  sleep "$POLL"
done

echo "Adapter ready. Publishing..."
bash "$FINETUNE/hf/publish_model.sh"
bash "$FINETUNE/convert_adapter.sh" "$ADAPTER" \
  "$FINETUNE/qwen2.5-7b-laravel-coder-lora/adapters/qwen-laravel-lora.gguf" || true
SKIP_TRAIN=1 SKIP_EVAL=1 bash "$FINETUNE/qwen2.5-7b-laravel-coder-lora/publish.sh"

echo "Published HF + Ollama."
