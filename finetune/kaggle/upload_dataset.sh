#!/bin/bash
# Upload Laravel training datasets to Kaggle.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
ROOT="$(cd "$FINETUNE/.." && pwd)"
STAGING="$DIR/staging"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"
# shellcheck source=/dev/null
source "$DIR/load_auth.sh"

echo "==> Rebuild training data"
python3 "$ROOT/shared/build_training_data.py"
python3 "$FINETUNE/prepare_dataset.py"
python3 "$FINETUNE/export_chat_dataset.py"

rm -rf "$STAGING"
mkdir -p "$STAGING/raw" "$STAGING/chat" "$STAGING/lora"

cp "$ROOT/shared/data/meta.json" "$STAGING/meta.json"
cp "$ROOT/shared/data/few_shot_examples.json" "$STAGING/few_shot_examples.json"
cp "$ROOT/shared/data/laravel_knowledge.md" "$STAGING/laravel_knowledge.md"
cp "$ROOT/shared/data/laravel_training.jsonl" "$STAGING/raw/laravel_training.jsonl"
cp "$FINETUNE/data/laravel_training_chat.jsonl" "$STAGING/chat/laravel_training_chat.jsonl"
cp "$FINETUNE/data/laravel_train.jsonl" "$STAGING/lora/laravel_train.jsonl"
cp "$FINETUNE/data/laravel_eval.jsonl" "$STAGING/lora/laravel_eval.jsonl"
cp "$FINETUNE/data/laravel_train.jsonl" "$STAGING/laravel_train.jsonl"
cp "$FINETUNE/data/laravel_eval.jsonl" "$STAGING/laravel_eval.jsonl"
cp "$DIR/dataset_README.md" "$STAGING/README.md"

cat > "$STAGING/dataset-metadata.json" <<EOF
{
  "title": "Laravel Coder LoRA Train",
  "id": "${KAGGLE_USERNAME}/${KAGGLE_DATASET_SLUG}",
  "licenses": [{"name": "CC0-1.0"}]
}
EOF

echo "==> Upload to Kaggle: ${KAGGLE_USERNAME}/${KAGGLE_DATASET_SLUG}"
# Root-level JSONL files mount directly; subdirs uploaded as .tar (not auto-extracted).
UPLOAD_ARGS=(-p "$STAGING" -m "800 train samples — flat lora paths" -r skip)
if kaggle datasets list -m -s "${KAGGLE_USERNAME}/${KAGGLE_DATASET_SLUG}" 2>/dev/null | grep -q "${KAGGLE_DATASET_SLUG}"; then
  kaggle datasets version "${UPLOAD_ARGS[@]}"
else
  kaggle datasets create "${UPLOAD_ARGS[@]}"
fi

echo "Published: https://www.kaggle.com/datasets/${KAGGLE_USERNAME}/${KAGGLE_DATASET_SLUG}"
