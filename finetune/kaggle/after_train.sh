#!/bin/bash
# After Kaggle GPU training: download kernel output → publish weights → push inference kernel.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"
# shellcheck source=/dev/null
source "$DIR/load_auth.sh"

OUT="${KAGGLE_OUTPUT:-$FINETUNE/kaggle_output}"
mkdir -p "$OUT"

echo "==> Download kernel output: ${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN}"
if ! kaggle kernels output "${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN}" -p "$OUT" -o; then
  echo "Full download failed — retrying merged model files only..."
  kaggle kernels output "${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN}" -p "$OUT" \
    --file-pattern "qwen-laravel-coder/.*" -o || true
fi

if [[ ! -s "$OUT/qwen-laravel-coder/model.safetensors" ]] && ! ls "$OUT/qwen-laravel-coder"/model-*.safetensors &>/dev/null; then
  echo "Merged weights incomplete — will publish adapter if available"
fi

echo "==> Publish weights dataset"
KAGGLE_OUTPUT="$OUT" bash "$DIR/publish_model.sh"

echo "==> Push inference kernel"
kaggle kernels push -p "$DIR/inference"

echo ""
echo "Done."
echo "  Weights:  https://www.kaggle.com/datasets/${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}"
echo "  Inference: https://www.kaggle.com/code/${KAGGLE_USERNAME}/${KAGGLE_KERNEL_INFERENCE}"
