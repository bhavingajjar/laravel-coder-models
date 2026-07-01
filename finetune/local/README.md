# Local LoRA training

Train on **this machine** when you have a CUDA GPU (or CPU as fallback — slow).

```bash
cd /var/www/html/ollama
pip install -r finetune/requirements.txt   # once
bash finetune/local/train.sh
```

## Options

| Env var | Default | Description |
|---------|---------|-------------|
| `PUSH_TO_HUB` | `0` | Set `1` to upload adapter to `HUB_MODEL_ID` after training |
| `BASE_MODEL` | `Qwen/Qwen2.5-Coder-7B-Instruct` | HF base model |
| `ADAPTER_DIR` | `qwen2.5-7b-laravel-coder-lora/adapters/qwen-laravel-lora` | Output path |

## GPU vs CPU

- **CUDA available** → `bfloat16`, `device_map=auto` (~30–90 min for 150 samples)
- **No CUDA** → `float32` on CPU (hours)

## After training

```bash
bash finetune/convert_adapter.sh
SKIP_TRAIN=1 ./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```
