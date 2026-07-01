# Kaggle — Laravel Coder (GPU training)

Local CPU training is not supported on this machine (7B OOM). Use Kaggle GPU instead.

## One-time setup

```bash
cp finetune/kaggle/auth.example finetune/kaggle/auth.local
# Edit auth.local: export KAGGLE_API_TOKEN="KGAT_..."
pip install kaggle   # or: finetune/.venv/bin/pip install kaggle
```

## Publish dataset + push training kernel

```bash
bash finetune/kaggle/all.sh
```

## Train on Kaggle GPU

1. Open [qwen-laravel-coder-train](https://www.kaggle.com/code/bhavingajjar22/qwen-laravel-coder-train)
2. **Settings → Accelerator → GPU** (T4 is fine)
3. **Run All** (~1–3 h for 800 samples)

Output: `/kaggle/working/qwen-laravel-coder/` (merged full model)

## After training

```bash
bash finetune/kaggle/after_train.sh
```

This downloads kernel output, publishes weights dataset, and pushes the inference notebook.

## Resources

| Resource | Slug |
|----------|------|
| Dataset | `bhavingajjar22/laravel-coder-lora-train` |
| Train kernel | `bhavingajjar22/qwen-laravel-coder-train` |
| Weights | `bhavingajjar22/qwen-laravel-coder-weights` |
| Inference | `bhavingajjar22/qwen-laravel-coder-inference` |

## Manual steps

```bash
bash finetune/kaggle/upload_dataset.sh
kaggle kernels push -p finetune/kaggle/train_kernel
kaggle kernels output bhavingajjar22/qwen-laravel-coder-train -p finetune/kaggle_output
bash finetune/kaggle/publish_model.sh
kaggle kernels push -p finetune/kaggle/inference
```
