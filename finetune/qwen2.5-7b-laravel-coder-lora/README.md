# qwen2.5-7b-laravel-coder-lora

**Bob (LoRA)** — experimental fine-tuned variant of [qwen2.5-7b-laravel-coder](https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder) with a LoRA adapter trained on curated Laravel docs (v10–v13).

## vs modelfile/ (production)

| | modelfile/ | finetune/ (this model) |
|--|------------|------------------------|
| **Ollama** | `bhavingajjar/qwen2.5-7b-laravel-coder` | `bhavingajjar/qwen2.5-7b-laravel-coder-lora` |
| **Method** | System prompt + few-shots | LoRA weights + shorter system prompt |
| **Status** | Production / fallback | Experimental |

If LoRA underperforms, use the production model — it is never overwritten.

## Quick start

```bash
ollama pull bhavingajjar/qwen2.5-7b-laravel-coder-lora
ollama run bhavingajjar/qwen2.5-7b-laravel-coder-lora
```

**Model page:** https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder-lora

## Train and publish (local)

```bash
cd /var/www/html/ollama
pip install -r finetune/requirements.txt
SKIP_TRAIN=0 ./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```

Minimal CPU settings (Intel Iris Xe): rank 4, 1 epoch, 50–150 QA pairs. Training may take hours on CPU.

## License

- [Qwen2.5-Coder](https://github.com/QwenLM/Qwen2.5-Coder) — Apache 2.0
- [Laravel documentation](https://github.com/laravel/docs) — MIT
- LoRA adapter — Apache 2.0
