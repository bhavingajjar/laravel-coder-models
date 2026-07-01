#!/bin/bash
# Upload dataset + push GPU training kernel.
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
echo "Run GPU on Kaggle: https://www.kaggle.com/code/${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN}"
echo "After completion, download output:"
echo "  kaggle kernels output ${KAGGLE_USERNAME}/${KAGGLE_KERNEL_TRAIN} -p $FINETUNE/kaggle_output"
echo "Then: bash $DIR/publish_model.sh"
