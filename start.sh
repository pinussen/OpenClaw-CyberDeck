#!/bin/bash
# Start CyberDeck web server

cd ~/.openclaw/workspace-dev/cyberdeck

# Activate venv
source .venv/bin/activate

# Start server
echo "Starting CyberDeck Web Server..."
echo "URL: http://localhost:5000"
echo ""
echo "Available endpoints:"
echo "  /                    - Main UI"
echo "  /issues              - Issues manager"
echo "  /dashboard           - Issues dashboard"
echo "  /api/activities      - Activity feed"
echo "  /api/queue           - Queue status"
echo "  /api/issues          - Issues API"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 web_server_fixed.py --live --port 5000
