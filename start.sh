#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🧠 Starting MicroGPT Web Server (Local CPU & < 100MB)"
echo "=========================================================="

# Check if model weights exist, if not train briefly
if [ ! -f "weights/micro_model.npz" ]; then
    echo "Model weights not found. Training quick baseline model..."
    python3 train.py --epochs 25 --batch_size 4 --lr 0.003
fi

echo "Starting Flask web server on http://localhost:5000 ..."
python3 app.py
