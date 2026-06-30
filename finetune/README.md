# finetune/ — Experimental LoRA Bob

Optional accuracy upgrade via LoRA fine-tuning. **If this fails, use `../modelfile/` — production is unchanged.**

## Upload destination

Fine-tuned models push to **ollama.com** under your account:

| Model | URL |
|-------|-----|
| Production (modelfile/) | https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder |
| LoRA (finetune/) | https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder-lora |

## Pipeline (Qwen first)

```bash
cd /var/www/html/ollama

# 1. Curate tiny dataset from shared/data/
python3 finetune/prepare_dataset.py

# 2. Train (CPU — slow on Intel Iris Xe; 16GB+ RAM recommended)
pip install -r finetune/requirements.txt
python3 finetune/train_lora_minimal.py

# 3. Convert adapter to GGUF (requires llama.cpp) or use Safetensors path
bash finetune/convert_adapter.sh

# 4. Evaluate vs modelfile Bob, then publish if LoRA wins
./finetune/qwen2.5-7b-laravel-coder-lora/publish.sh
```

## Minimal training settings

| Setting | Value |
|---------|-------|
| HF base | `Qwen/Qwen2.5-Coder-7B-Instruct` |
| Device | CPU (Iris Xe not used for training) |
| LoRA | r=4, alpha=8, 1 epoch |
| Data | 50–150 curated pairs |

## Colab fallback

If local CPU is too slow or OOM: train in Google Colab, download adapter to `finetune/qwen2.5-7b-laravel-coder-lora/adapters/`, then run `publish.sh` with `SKIP_TRAIN=1`.

## Files

| Script | Purpose |
|--------|---------|
| `prepare_dataset.py` | Filter high-quality train/eval JSONL |
| `train_lora_minimal.py` | CPU PEFT LoRA training |
| `convert_adapter.sh` | Safetensors → GGUF for Ollama |
| `evaluate.py` | A/B modelfile vs LoRA |
| `build_lora_modelfile.py` | Generate FROM + ADAPTER Modelfile |
