# Laravel Coder Models (Bob)

Custom Ollama models — **Bob**, a senior PHP/Laravel coding assistant — built on different base LLMs with version-aware [Laravel documentation](https://github.com/laravel/docs) knowledge (v10–v13).

## Two paths

| Folder | Method | Status |
|--------|--------|--------|
| **[modelfile/](modelfile/)** | Prompt-only (SYSTEM + few-shots) | **Production / fallback** |
| **[finetune/](finetune/)** | LoRA adapter + shorter prompt | **Experimental** |

If fine-tuning fails or underperforms, `modelfile/` models are unchanged.

## Models

| Model | Path | Ollama |
|-------|------|--------|
| `qwen2.5-7b-laravel-coder` | [modelfile/](modelfile/qwen2.5-7b-laravel-coder/) | [ollama.com](https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder) |
| `codellama-7b-laravel-coder` | [modelfile/](modelfile/codellama-7b-laravel-coder/) | [ollama.com](https://ollama.com/bhavingajjar/codellama-7b-laravel-coder) |
| `deepseek-v2-16b-laravel-coder` | [modelfile/](modelfile/deepseek-v2-16b-laravel-coder/) | [ollama.com](https://ollama.com/bhavingajjar/deepseek-v2-16b-laravel-coder) |
| `qwen2.5-7b-laravel-coder-lora` | [finetune/](finetune/qwen2.5-7b-laravel-coder-lora/) | [ollama.com](https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder-lora) |

## Quick start

```bash
# Production (prompt-only Bob)
ollama run bhavingajjar/qwen2.5-7b-laravel-coder

# Experimental LoRA (after train + publish)
ollama run bhavingajjar/qwen2.5-7b-laravel-coder-lora
```

## Version-aware behavior

Bob supports **Laravel 10.x through 13.x**. Before answering:

1. Detects the Laravel version from `composer.json`, `bootstrap/app.php`, or code patterns
2. States the detected version explicitly
3. Provides version-correct code and guidance

## Repository layout

```
.
├── README.md
├── laravel-docs/              # Official Laravel docs v10–v13
├── shared/                    # build_training_data.py, build_modelfile.py, data/
├── modelfile/                 # Production — prompt-only Bob (3 models)
└── finetune/                  # Experimental — LoRA (Qwen first)
```

## Publish production models

```bash
./modelfile/qwen2.5-7b-laravel-coder/publish.sh
./modelfile/codellama-7b-laravel-coder/publish.sh
./modelfile/deepseek-v2-16b-laravel-coder/publish.sh
```

## Fine-tune (experimental)

```bash
pip install -r finetune/requirements.txt
python3 finetune/prepare_dataset.py
python3 finetune/train_lora_minimal.py          # CPU — slow on Intel Iris Xe
./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```

See [finetune/README.md](finetune/README.md) for Colab fallback and adapter conversion.

## Updating docs

```bash
git -C laravel-docs/13.x pull
./modelfile/qwen2.5-7b-laravel-coder/publish.sh
```
