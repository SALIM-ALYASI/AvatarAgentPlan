#!/bin/bash
# start_web.sh - Launch the Avatar Agent Web UI

# Get absolute path
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Source conda
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate avatar

echo "Starting Avatar Agent Web Interface on http://localhost:8000"
cd "$SCRIPT_DIR"
uvicorn app:app --host 127.0.0.1 --port 8000
