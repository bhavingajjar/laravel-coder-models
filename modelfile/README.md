# modelfile/ — Production Bob (prompt-only)

Primary path for all Bob Laravel coder models. **No weight changes** — uses system prompt, knowledge digest, and few-shot examples via Modelfile.

If fine-tuning in `../finetune/` fails or underperforms, these models remain unchanged and production-ready.

## Models

| Model | Publish | Ollama |
|-------|---------|--------|
| `qwen2.5-7b-laravel-coder` | `./qwen2.5-7b-laravel-coder/publish.sh` | [ollama.com](https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder) |
| `codellama-7b-laravel-coder` | `./codellama-7b-laravel-coder/publish.sh` | [ollama.com](https://ollama.com/bhavingajjar/codellama-7b-laravel-coder) |
| `deepseek-v2-16b-laravel-coder` | `./deepseek-v2-16b-laravel-coder/publish.sh` | [ollama.com](https://ollama.com/bhavingajjar/deepseek-v2-16b-laravel-coder) |

## Publish

```bash
cd /var/www/html/ollama
./modelfile/qwen2.5-7b-laravel-coder/publish.sh
```

Rebuilds shared training data from `../shared/`, generates Modelfile, creates and pushes to `bhavingajjar`.
