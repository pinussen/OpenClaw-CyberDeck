#!/usr/bin/env python3
"""
CyberDeck Web Server - Flask + SocketIO for PinePhone interface
Simplified version without eventlet dependency
"""

import os
import sys
import json
import threading
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from lib.database import get_db

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'cyberdeck-secret-key')

# SocketIO with threading (no eventlet needed)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Demo mode display components (no PIL dependencies)
class DemoMolty:
    """Simplified Molty for demo mode."""
    def __init__(self):
        self.state = 'idle'
    def set_state(self, state):
        self.state = state
    def get_state(self):
        return self.state
    def get_state_info(self):
        return {"state": self.state, "label": self.state.capitalize()}
    def render_svg(self):
        return f'<svg viewBox="0 0 200 200"><text x="100" y="100" text-anchor="middle" fill="#00f5d4">🦞 {self.state}</text></svg>'

class DemoActivityFeed:
    """Simplified activity feed."""
    def __init__(self):
        self.entries = []
    def add_entry(self, type_, title, detail="", status="done"):
        self.entries.append({
            "type": type_, "title": title, "detail": detail,
            "status": status, "timestamp": datetime.now().isoformat()
        })
        if len(self.entries) > 50:
            self.entries = self.entries[-50:]
    def clear(self):
        self.entries = []
    def get_recent(self, limit=10):
        return list(reversed(self.entries[-limit:]))

class DemoDisplay:
    """Simplified display."""
    def __init__(self):
        self.molty = DemoMolty()
        self.activity_feed = DemoActivityFeed()
        self._status = "Ready"
    def add_activity(self, type_, title, detail="", status="done"):
        self.activity_feed.add_entry(type_, title, detail, status)
    def add_message(self, role, content):
        self.activity_feed.add_entry("message", role, content[:50])
    def set_molty_state(self, state):
        self.molty.set_state(state)
    def set_status(self, text):
        self._status = text
    def get_state_dict(self):
        return {
            "molty_state": self.molty.get_state(),
            "status_text": self._status,
            "activities": self.activity_feed.get_recent(20),
            "timestamp": datetime.now().isoformat()
        }

# Global display instance
display = DemoDisplay()

# Flask Routes
@app.route('/')
def index():
    return render_template('cyberdeck.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        "connected": True,
        "demo_mode": True,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/display-state')
def api_display_state():
    return jsonify(display.get_state_dict())

@app.route('/api/command', methods=['POST'])
def api_command():
    data = request.get_json() or {}
    cmd = data.get('command', '')
    
    if cmd == 'clear':
        display.activity_feed.clear()
        return jsonify({"success": True, "message": "Cleared"})
    elif cmd == 'demo':
        import random
        demos = [
            ('tool', 'Search executed', 'Found 5 results'),
            ('message', 'Assistant', 'Hello from OpenClaw!'),
            ('status', 'Task done', 'All operations complete'),
        ]
        t, title, detail = random.choice(demos)
        display.add_activity(t, title, detail)
        display.set_molty_state(random.choice(['idle', 'working', 'success']))
        
        # Broadcast to all clients
        socketio.emit('activity', {
            'type': t, 'title': title, 'message': detail,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({"success": True, "message": "Demo triggered"})
    elif cmd == 'status':
        return jsonify({"success": True, "status": display.get_state_dict()})
    
    return jsonify({"success": False, "error": f"Unknown command: {cmd}"})

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    print(f"[Server] Client connected")
    emit('status', {"connected": True, "demo_mode": True})
    emit('display_state', display.get_state_dict())

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[Server] Client disconnected")

@socketio.on('command')
def handle_command(data):
    cmd = data.get('command') if isinstance(data, dict) else data
    if cmd == 'get_state':
        emit('display_state', display.get_state_dict())

@socketio.on('ping')
def handle_ping():
    emit('pong', {'timestamp': datetime.now().isoformat()})

# Dashboard route
@app.route('/dashboard')
def dashboard():
    """Render cyberdeck dashboard with issues overview."""
    return render_template('dashboard.html')

@app.route('/issues/<key>/edit')
def edit_issue(key):
    """Render edit page for issue."""
    return render_template('edit.html')

@app.route('/api/dashboard/summary')
def dashboard_summary():
    """Get dashboard summary"""
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM issues 
            WHERE status IN ('todo', 'in_progress', 'blocked')
        """)
        open_count = cur.fetchone()[0]
        
        cur.execute("""
            SELECT i.key, i.title, i.status, i.priority, i.labels, 
                   COALESCE(u.display_name, u.username) as assignee,
                   parent.key as parent_key
            FROM issues i
            LEFT JOIN issue_users u ON u.id = i.assignee_user_id
            LEFT JOIN issue_links il ON il.to_issue_id = i.id AND il.link_type = 'subtask'
            LEFT JOIN issues parent ON parent.id = il.from_issue_id
            WHERE i.status IN ('todo', 'in_progress', 'blocked')
            ORDER BY 
                CASE WHEN parent.key IS NULL THEN 0 ELSE 1 END,
                i.created_at DESC
            LIMIT 50
        """)
        
        recent = []
        for row in cur.fetchall():
            recent.append({
                'key': row[0],
                'title': row[1],
                'status': row[2],
                'priority': row[3],
                'labels': row[4] or [],
                'assignee': row[5],
                'parent_key': row[6]
            })
        
        return jsonify({
            'ok': True,
            'summary': {'total_issues': open_count},
            'recent_issues': recent
        })


# Issues routes
@app.route('/issues')
def issues():
    """Render issues viewer."""
    return render_template('issues_full.html')

@app.route('/api/issues')
def api_issues():
    """Get issues with filters"""
    with get_db().cursor() as cur:
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        query = """
            SELECT i.key, i.title, i.status, i.priority, i.created_at, i.labels, 
                   COALESCE(u.display_name, u.username) as assignee
            FROM issues i
            LEFT JOIN issue_users u ON u.id = i.assignee_user_id
        """
        params = []
        
        if status:
            query += " WHERE status = %s"
            params.append(status)
        elif priority:
            query += " WHERE priority = %s"
            params.append(priority)
        
        query += " ORDER BY created_at DESC LIMIT 500"
        
        cur.execute(query, params)
        
        issues_list = []
        for row in cur.fetchall():
            issues_list.append({
                'key': row[0],
                'title': row[1],
                'status': row[2],
                'priority': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'labels': row[5] or [],
                'assignee': row[6]
            })
        
        return jsonify({'ok': True, 'issues': issues_list})

@app.route('/api/issues/<key>')
def api_issue_detail(key):
    """Get single issue with events"""
    with get_db().cursor() as cur:
        # Get issue - join with issue_users for assignee
        cur.execute("""
            SELECT i.id, i.key, i.title, i.description, i.status, i.priority,
                   u.username as assignee_user_id, i.reporter, i.created_at, i.updated_at,
                   i.labels, i.metadata
            FROM issues i
            LEFT JOIN issue_users u ON u.id = i.assignee_user_id
            WHERE i.key = %s
        """, (key,))
        
        row = cur.fetchone()
        if not row:
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        
        issue_id = row[0]
        
        issue = {
            'key': row[1],
            'title': row[2],
            'description': row[3],
            'status': row[4],
            'priority': row[5],
            'assignee_user_id': row[6],
            'reporter': row[7],
            'created_at': row[8].isoformat() if row[8] else None,
            'updated_at': row[9].isoformat() if row[9] else None,
            'labels': row[10] or [],
            'metadata': row[11] or {}
        }
        
        # Get events - join with issues to get UUID from key
        cur.execute("""
            SELECT e.id, e.event_type, e.payload as content, e.created_at
            FROM issue_events e
            JOIN issues i ON i.id = e.issue_id
            WHERE i.key = %s
            ORDER BY e.created_at DESC
        """, (key,))
        
        events = []
        for row in cur.fetchall():
            events.append({
                'id': row[0],
                'type': row[1],
                'content': row[2],
                'created_at': row[3].isoformat() if row[3] else None
            })
        
        issue['events'] = events
        
        # Get subtasks
        cur.execute("""
            SELECT i.key, i.title, i.status
            FROM issue_links il
            JOIN issues i ON i.id = il.to_issue_id
            WHERE il.from_issue_id = %s AND il.link_type = 'subtask'
        """, (issue_id,))
        
        subtasks = []
        for row in cur.fetchall():
            subtasks.append({
                'key': row[0],
                'title': row[1],
                'status': row[2]
            })
        issue['subtasks'] = subtasks
        
        # Get parent
        cur.execute("""
            SELECT i.key, i.title, i.status
            FROM issue_links il
            JOIN issues i ON i.id = il.from_issue_id
            WHERE il.to_issue_id = %s AND il.link_type = 'subtask'
        """, (issue_id,))
        
        row = cur.fetchone()
        if row:
            issue['parent'] = {'key': row[0], 'title': row[1], 'status': row[2]}
        else:
            issue['parent'] = None
        
        return jsonify({'ok': True, 'issue': issue})

@app.route('/api/issues/<key>/update', methods=['POST'])
def api_update_issue(key):
    """Update issue fields"""
    data = request.get_json()
    
    valid_fields = {'status', 'priority', 'title', 'assignee_user_id', 'labels'}
    updates = {}
    for field in valid_fields:
        if field in data:
            updates[field] = data[field]
    
    if not updates:
        return jsonify({'ok': False, 'error': 'No valid fields to update'}), 400
    
    with get_db().cursor() as cur:
        # Handle assignee_user_id - convert username to UUID if needed
        if 'assignee_user_id' in updates and updates['assignee_user_id']:
            user_val = updates['assignee_user_id']
            # If it looks like a username (not a UUID), look up the UUID
            if '-' not in str(user_val):
                cur.execute("SELECT id FROM issue_users WHERE username = %s", (user_val,))
                row = cur.fetchone()
                if row:
                    updates['assignee_user_id'] = str(row[0])
        
        # Update issue
        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        params = list(updates.values()) + [key]
        
        cur.execute(f"""
            UPDATE issues SET {set_clause}, updated_at = NOW()
            WHERE key = %s
        """, params)
        
        # Log event
        event_type = 'update'
        content = ", ".join([f"{k}={v}" for k, v in updates.items()])
        
        cur.execute("""
            INSERT INTO issue_events (issue_id, event_type, payload, actor)
            SELECT id, %s, %s::jsonb, 'system' FROM issues WHERE key = %s
        """, (event_type, json.dumps({"changes": content}), key))
    
    return jsonify({'ok': True, 'message': f'Updated {key}'})

@app.route('/api/issues/<key>/comment', methods=['POST'])
def api_add_comment(key):
    """Add comment to issue"""
    data = request.get_json()
    comment = data.get('comment', '').strip()
    
    if not comment:
        return jsonify({'ok': False, 'error': 'No comment'}), 400
    
    with get_db().cursor() as cur:
        cur.execute("""
            INSERT INTO issue_events (issue_id, event_type, payload, actor)
            SELECT id, %s, %s::jsonb, 'system' FROM issues WHERE key = %s
        """, ('comment', json.dumps({"text": comment}), key))
    
    return jsonify({'ok': True, 'message': 'Comment added'})

@app.route('/api/issues/<key>/comment/<int:event_id>', methods=['PUT', 'POST'])
def api_update_comment(key, event_id):
    """Update existing comment"""
    data = request.get_json()
    new_text = data.get('comment', '').strip()
    
    if not new_text:
        return jsonify({'ok': False, 'error': 'No comment text'}), 400
    
    with get_db().cursor() as cur:
        # Verify the event belongs to this issue and is a comment
        cur.execute("""
            UPDATE issue_events e
            SET payload = jsonb_set(payload, '{text}', %s::jsonb)
            FROM issues i
            WHERE e.id = %s AND e.event_type = 'comment'
            AND e.issue_id = i.id AND i.key = %s
        """, (json.dumps(new_text), event_id, key))
        
        if cur.rowcount == 0:
            return jsonify({'ok': False, 'error': 'Comment not found'}), 404
    
    return jsonify({'ok': True, 'message': 'Comment updated'})

@app.route('/api/issues/<key>/comment/<int:event_id>', methods=['DELETE'])
def api_delete_comment(key, event_id):
    """Delete a comment"""
    with get_db().cursor() as cur:
        cur.execute("""
            DELETE FROM issue_events e
            USING issues i
            WHERE e.id = %s AND e.event_type = 'comment'
            AND e.issue_id = i.id AND i.key = %s
        """, (event_id, key))
        
        if cur.rowcount == 0:
            return jsonify({'ok': False, 'error': 'Comment not found'}), 404
    
    return jsonify({'ok': True, 'message': 'Comment deleted'})

@app.route('/api/issues/create', methods=['POST'])
def api_create_issue():
    """Create new issue"""
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'ok': False, 'error': 'Title required'}), 400
    
    with get_db().cursor() as cur:
        cur.execute("""
            INSERT INTO issues (key, title, description, status, priority, labels)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING key
        """, (
            data.get('key', f'ISS-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
            data['title'],
            data.get('description', ''),
            data.get('status', 'todo'),
            data.get('priority', 'medium'),
            data.get('labels', [])
        ))
        
        key = cur.fetchone()[0]
    
    return jsonify({'ok': True, 'key': key})

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    
    ip = args.host if args.host != '0.0.0.0' else '192.168.2.22'
    
    print(f"""╔══════════════════════════════════════════════════╗
║     OpenClaw CyberDeck Web Server                ║
╠══════════════════════════════════════════════════╣
║  URLs:                                            ║
║  - Main:   http://{ip}:{args.port:<5}                 ║
║  - Dashboard: http://{ip}:{args.port:<5}<5>dashboard║
║  - Issues:  http://{ip}:{args.port:<5}<5>issues    ║
╚══════════════════════════════════════════════════╝""")
    
    socketio.run(app, host=args.host, port=args.port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
