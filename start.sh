#!/bin/bash
# Quick start script for CyberDeck Web

cd "$(dirname "$0")"

export FLASK_ENV=development
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Use venv Python
if [ -f .venv/bin/python ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python3"
fi

echo "Starting CyberDeck Web Server..."
echo "Access: http://192.168.2.22:5000"
echo "Local:  http://localhost:5000"
echo ""

$PYTHON web_server.py "$@"
