#!/bin/bash
# Source Kaggle auth from env or local gitignored file.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${KAGGLE_API_TOKEN:-}" && ! -f "$HOME/.kaggle/kaggle.json" ]]; then
  for f in "$DIR/auth.local" "$DIR/.credentials"; do
    if [[ -f "$f" ]]; then
      # shellcheck source=/dev/null
      source "$f"
      break
    fi
  done
fi

if [[ -z "${KAGGLE_API_TOKEN:-}" && ! -f "$HOME/.kaggle/kaggle.json" ]]; then
  echo "Kaggle auth missing. Copy auth.example to auth.local or export KAGGLE_API_TOKEN."
  exit 1
fi

export PATH="${PATH:-}:${DIR}/../.venv/bin"
