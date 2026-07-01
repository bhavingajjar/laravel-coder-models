#!/bin/bash
# Publish merged model weights as Kaggle dataset.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"
# shellcheck source=/dev/null
source "$DIR/load_auth.sh"

MERGED_LOCAL="${MERGED_LOCAL:-$FINETUNE/qwen2.5-7b-laravel-coder-lora/merged/qwen-laravel-coder}"
KAGGLE_OUT="${KAGGLE_OUTPUT:-$FINETUNE/kaggle_output}"
WEIGHTS_DIR="$DIR/weights_staging"

MERGED_SRC=""
if [[ -d "$KAGGLE_OUT/qwen-laravel-coder" ]] && [[ -s "$KAGGLE_OUT/qwen-laravel-coder/model.safetensors" || -f "$KAGGLE_OUT/qwen-laravel-coder/model-00001-of-"* ]]; then
  MERGED_SRC="$KAGGLE_OUT/qwen-laravel-coder"
elif [[ -d "$MERGED_LOCAL" ]] && [[ -s "$MERGED_LOCAL/model.safetensors" || -f "$MERGED_LOCAL/model-00001-of-"* ]]; then
  MERGED_SRC="$MERGED_LOCAL"
elif [[ -d "$KAGGLE_OUT/adapter/adapter_config.json" ]] || [[ -f "$KAGGLE_OUT/adapter/adapter_config.json" ]]; then
  ADAPTER_SRC="$KAGGLE_OUT/adapter"
elif [[ -f "$FINETUNE/$ADAPTER_DIR/adapter_config.json" ]]; then
  ADAPTER_SRC="$FINETUNE/$ADAPTER_DIR"
fi

if [[ -z "${MERGED_SRC:-}" ]]; then
  if [[ -n "${ADAPTER_SRC:-}" ]]; then
    echo "==> No merged weights — publishing LoRA adapter (load with base model)"
    WEIGHTS_DIR="$DIR/weights_staging"
    rm -rf "$WEIGHTS_DIR"
    mkdir -p "$WEIGHTS_DIR/qwen-laravel-coder-adapter"
    cp -a "$ADAPTER_SRC/." "$WEIGHTS_DIR/qwen-laravel-coder-adapter/"
    cp "$DIR/MODEL_README.md" "$WEIGHTS_DIR/README.md"
    cat > "$WEIGHTS_DIR/dataset-metadata.json" <<EOF
{
  "title": "Qwen2.5-7B Laravel Coder Weights",
  "id": "${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}",
  "licenses": [{"name": "apache-2.0"}]
}
EOF
    echo "==> Publish adapter dataset: ${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}"
    UPLOAD_ARGS=(-p "$WEIGHTS_DIR" -m "LoRA adapter — Laravel Coder" -r tar)
    if kaggle datasets list -m -s "${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}" 2>/dev/null | grep -q "${KAGGLE_WEIGHTS_SLUG}"; then
      kaggle datasets version "${UPLOAD_ARGS[@]}"
    else
      kaggle datasets create "${UPLOAD_ARGS[@]}"
    fi
    echo "https://www.kaggle.com/datasets/${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}"
    exit 0
  fi
  echo "No merged model or adapter. Run training first."
  exit 1
fi

rm -rf "$WEIGHTS_DIR"
mkdir -p "$WEIGHTS_DIR/qwen-laravel-coder"
cp -a "$MERGED_SRC/." "$WEIGHTS_DIR/qwen-laravel-coder/"
cp "$DIR/MODEL_README.md" "$WEIGHTS_DIR/README.md"

cat > "$WEIGHTS_DIR/dataset-metadata.json" <<EOF
{
  "title": "Qwen2.5-7B Laravel Coder Weights",
  "id": "${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}",
  "licenses": [{"name": "apache-2.0"}]
}
EOF

echo "==> Publish weights dataset: ${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}"
UPLOAD_ARGS=(-p "$WEIGHTS_DIR" -m "Merged Qwen2.5-7B Laravel Coder" -r tar)
if kaggle datasets list -m -s "${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}" 2>/dev/null | grep -q "${KAGGLE_WEIGHTS_SLUG}"; then
  kaggle datasets version "${UPLOAD_ARGS[@]}"
else
  kaggle datasets create "${UPLOAD_ARGS[@]}"
fi

echo "https://www.kaggle.com/datasets/${KAGGLE_USERNAME}/${KAGGLE_WEIGHTS_SLUG}"
