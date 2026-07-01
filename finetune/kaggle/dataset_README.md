# Laravel Coder LoRA — training data (Kaggle)

Same layout as Hugging Face dataset `bhavin-gajjar/laravel-coder-lora-train`.

| Path | Rows | Schema |
|------|------|--------|
| `raw/laravel_training.jsonl` | ~2000+ | instruction / input / output |
| `chat/laravel_training_chat.jsonl` | ~2000+ | messages |
| `lora/laravel_train.jsonl` | 800 | messages (train) |
| `lora/laravel_eval.jsonl` | 40 | messages (eval) |

Mount in kernels: `/kaggle/input/laravel-coder-lora-train/lora/laravel_train.jsonl`
