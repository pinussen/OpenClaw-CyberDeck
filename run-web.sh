#!/bin/bash
# CyberDeck Web Server startup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for virtualenv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements-web.txt

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults
export FLASK_APP=web_server.py
export FLASK_ENV=development

# Start server
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     OpenClaw CyberDeck Web Server        ║"
echo "╠══════════════════════════════════════════╣"
echo "║  Access: http://$(hostname -I | awk '{print $1}'):5000"
echo "║  Local: http://localhost:5000             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

python3 web_server.py "$@"
