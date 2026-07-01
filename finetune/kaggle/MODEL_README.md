# Qwen2.5-7B Laravel Coder — merged weights

Fine-tuned from **Qwen/Qwen2.5-Coder-7B-Instruct** for Laravel v10–v13.

## Load in Kaggle

```python
MODEL = "/kaggle/input/qwen-laravel-coder-weights/qwen-laravel-coder"
```

## Load from Hugging Face

```python
MODEL = "bhavin-gajjar/qwen-laravel-coder"
```

## Training reference (LoRA — documentation only)

| Setting | Value |
|---------|-------|
| LoRA r | 4 |
| LoRA alpha | 8 |
| targets | q_proj, v_proj |
| samples | 800 |
| epochs | 1 |

This dataset contains the **merged full model**, not a separate PEFT adapter.
