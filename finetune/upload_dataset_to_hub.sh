#!/bin/bash
exec "$(cd "$(dirname "$0")" && pwd)/hf/upload_datasets.sh" "$@"
