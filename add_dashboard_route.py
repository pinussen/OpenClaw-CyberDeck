#!/usr/bin/env python3
"""Add dashboard to cyberdeck web server"""

import sys
sys.path.insert(0, '/home/bjwl/.openclaw/workspace-dev')

from flask import render_template
import os

# Read web_server.py
with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server.py', 'r') as f:
    content = f.read()

# Add dashboard route after issues routes
if '@app.route(\'/issues\')' not in content:
    print("Issues route not found yet - waiting for previous changes...")
    sys.exit(1)

# Find the dashboard routes section to add after
insert_marker = '''@app.route('/api/issues/<key>')
def api_issue_detail(key):'''

new_routes = '''

@app.route('/dashboard')
def dashboard():
    """Render cyberdeck dashboard with issues overview."""
    return render_template('dashboard.html')

'''

content = content.replace(insert_marker, insert_marker + new_routes)

# Write back
with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server.py', 'w') as f:
    f.write(content)

print("✅ Dashboard route added to web_server.py")
