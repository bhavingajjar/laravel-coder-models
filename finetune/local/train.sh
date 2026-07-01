#!/bin/bash
# Local LoRA training (auto: CUDA GPU if present, else CPU).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
ROOT="$(cd "$FINETUNE/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
PYTHON="${PYTHON:-$VENV/bin/python3}"
PUSH_TO_HUB="${PUSH_TO_HUB:-0}"

if [[ ! -x "$PYTHON" ]]; then
  echo "Missing venv. Run: pip install -r $FINETUNE/requirements.txt"
  exit 1
fi

echo "==> Rebuild training data"
python3 "$ROOT/shared/build_training_data.py"
python3 "$FINETUNE/prepare_dataset.py"

TRAIN_ARGS=(
  --train "$FINETUNE/$TRAIN_FILE"
  --output "$FINETUNE/$ADAPTER_DIR"
  --model "$BASE_MODEL"
  --epochs "$EPOCHS"
  --max-seq-length "$MAX_SEQ_LENGTH"
)

if [[ "$PUSH_TO_HUB" == "1" ]]; then
  TRAIN_ARGS+=(--push-to-hub --hub-model-id "$HUB_MODEL_ID")
fi

echo "==> Local LoRA training"
"$PYTHON" "$DIR/train.py" "${TRAIN_ARGS[@]}"

echo ""
echo "Adapter: $FINETUNE/$ADAPTER_DIR"
echo "Next: bash $FINETUNE/convert_adapter.sh"
echo "      SKIP_TRAIN=1 $FINETUNE/qwen2.5-7b-laravel-coder-lora/publish.sh"
