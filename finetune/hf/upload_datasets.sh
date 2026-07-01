#!/bin/bash
# Upload full Laravel datasets to HF dataset repo + public bucket.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
ROOT="$(cd "$FINETUNE/.." && pwd)"
SHARED="$ROOT/shared/data"
DATA="$FINETUNE/data"
STAGING="$DIR/staging"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"

VENV="${VENV:-$FINETUNE/$VENV_DIR}"
HF="${HF:-$VENV/bin/hf}"

if [[ -z "${HF_TOKEN:-}" && -f "$HOME/.cache/huggingface/token" ]]; then
  export HF_TOKEN="$(cat "$HOME/.cache/huggingface/token")"
fi
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "Set HF_TOKEN or run: hf auth login"
  exit 1
fi

echo "==> Rebuild all Laravel training data (v10–v13 docs)"
python3 "$ROOT/shared/build_training_data.py"
python3 "$FINETUNE/prepare_dataset.py"
python3 "$FINETUNE/export_chat_dataset.py"

rm -rf "$STAGING"
mkdir -p "$STAGING/raw" "$STAGING/chat" "$STAGING/lora"

cp "$SHARED/meta.json" "$STAGING/meta.json"
cp "$SHARED/few_shot_examples.json" "$STAGING/few_shot_examples.json"
cp "$SHARED/laravel_knowledge.md" "$STAGING/laravel_knowledge.md"
cp "$SHARED/laravel_training.jsonl" "$STAGING/raw/laravel_training.jsonl"
cp "$DATA/laravel_training_chat.jsonl" "$STAGING/chat/laravel_training_chat.jsonl"
cp "$DATA/laravel_train.jsonl" "$STAGING/lora/laravel_train.jsonl"
cp "$DATA/laravel_eval.jsonl" "$STAGING/lora/laravel_eval.jsonl"
cp "$DATA/meta.json" "$STAGING/lora/meta.json"
cp "$DIR/dataset_README.md" "$STAGING/README.md"

echo "==> Create dataset repo: $DATASET_REPO"
"$HF" repo create "$DATASET_REPO" --repo-type dataset --exist-ok

echo "==> Upload to dataset repo"
"$HF" upload "$DATASET_REPO" "$STAGING" . --repo-type dataset \
  --delete "laravel_train.jsonl" --delete "laravel_eval.jsonl"

echo "==> Sync to bucket: $BUCKET_ID/$BUCKET_PREFIX"
"$HF" buckets sync "$STAGING" "hf://buckets/$BUCKET_ID/$BUCKET_PREFIX"

echo ""
echo "Dataset: https://huggingface.co/datasets/$DATASET_REPO"
echo "Bucket:  https://huggingface.co/buckets/$BUCKET_ID/$BUCKET_PREFIX"
