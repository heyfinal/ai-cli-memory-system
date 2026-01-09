#!/bin/bash
# Launch AI CLI Memory Dashboard

echo "🚀 Starting AI CLI Memory Dashboard..."

# Check if flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    brew install python-flask 2>/dev/null || pipx install flask
fi

# Launch dashboard
python3 ~/ai-cli-memory-system/scripts/dashboard.py
