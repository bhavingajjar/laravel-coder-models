#!/bin/bash
exec "$(cd "$(dirname "$0")" && pwd)/hf/download_adapter.sh" "$@"
