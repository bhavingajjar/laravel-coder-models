#!/bin/bash
# Kaggle-only pipeline: upload dataset → push GPU training kernel.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
FINETUNE="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$FINETUNE/lora/config.env"
# shellcheck source=/dev/null
source "$DIR/load_auth.sh"

bash "$DIR/upload_dataset.sh"

echo "==> Push GPU training kernel: ${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN}"
kaggle kernels push -p "$DIR/train_kernel" --accelerator NvidiaTeslaT4

echo ""
echo "=== Next: train on Kaggle GPU ==="
echo "1. Open: https://www.kaggle.com/code/${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN}"
echo "2. Settings → Accelerator → GPU T4 x2 (or any GPU)"
echo "3. Run All cells (~1-3 hours for 800 samples)"
echo ""
echo "=== After training completes ==="
echo "  bash finetune/kaggle/after_train.sh"
