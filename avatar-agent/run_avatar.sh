#!/bin/bash
set -e
# run_avatar.sh - Run SadTalker with one click

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <path_to_image> <path_to_audio> [quality]"
    echo "Example: $0 inputs/photo.jpg inputs/voice.wav high"
    exit 1
fi

IMAGE_PATH=$1
AUDIO_PATH=$2
QUALITY=${3:-fast}

# Get absolute paths to inputs
IMAGE_ABS=$(cd "$(dirname "$IMAGE_PATH")" && pwd)/$(basename "$IMAGE_PATH")
AUDIO_ABS=$(cd "$(dirname "$AUDIO_PATH")" && pwd)/$(basename "$AUDIO_PATH")

# Get absolute path to outputs folder
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
OUTPUT_DIR="$SCRIPT_DIR/outputs"

# Ensure outputs directory exists
mkdir -p "$OUTPUT_DIR"

# Source conda
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate avatar

# Change directory to sadtalker
cd "$SCRIPT_DIR/sadtalker"

echo "Running SadTalker..."
export PATH="/opt/homebrew/bin:$PATH"
export PYTORCH_ENABLE_MPS_FALLBACK=1
export IMAGEIO_FFMPEG_EXE=/opt/homebrew/bin/ffmpeg
if [ "$QUALITY" = "high" ]; then
    echo "Running SadTalker in HIGH QUALITY mode (4K + GFPGAN)..."
    python inference.py --driven_audio "$AUDIO_ABS" --source_image "$IMAGE_ABS" --result_dir "$OUTPUT_DIR" --enhancer gfpgan --size 1024 --preprocess full --still
else
    echo "Running SadTalker in FAST mode (Standard)..."
    python inference.py --driven_audio "$AUDIO_ABS" --source_image "$IMAGE_ABS" --result_dir "$OUTPUT_DIR"
fi
echo "Done! The output video is in $OUTPUT_DIR"
