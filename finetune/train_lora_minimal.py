#!/usr/bin/env python3
"""Backward-compat wrapper — use finetune/local/train.py instead."""
import subprocess
import sys
from pathlib import Path

script = Path(__file__).resolve().parent / "local" / "train.py"
raise SystemExit(subprocess.call([sys.executable, str(script), *sys.argv[1:]]))
