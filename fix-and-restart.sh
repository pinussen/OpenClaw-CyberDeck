#!/bin/bash
# Fix cyberdeck.service and restart

cat > /tmp/cyberdeck.service << 'EOF'
[Unit]
Description=CyberDeck Web Server for PinePhone
After=network.target

[Service]
Type=simple
User=bjwl
WorkingDirectory=/home/bjwl/.openclaw/workspace-dev/cyberdeck
Environment="PATH=/home/bjwl/.openclaw/workspace-dev/cyberdeck/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/bjwl/.openclaw/workspace-dev/cyberdeck/.venv/bin/python web_server.py --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

cp /tmp/cyberdeck.service /etc/systemd/system/cyberdeck.service
systemctl daemon-reload
systemctl restart cyberdeck.service
