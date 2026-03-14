#!/usr/bin/env python3
"""
Enhanced Issues Viewer with full CRUD functionality
"""

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
from lib.database import get_db

app = Flask(__name__)


@app.route('/')
def issues():
    return render_template('issues_full.html')


@app.route('/api/issues')
def api_issues():
    """Get issues with filters"""
    with get_db().cursor() as cur:
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        query = """
            SELECT key, title, status, priority, created_at, labels, assignee_agent
            FROM issues
        """
        params = []
        
        if status:
            query += " WHERE status = %s"
            params.append(status)
        elif priority:
            query += " WHERE priority = %s"
            params.append(priority)
        
        query += " ORDER BY created_at DESC LIMIT 50"
        
        cur.execute(query, params)
        
        issues = []
        for row in cur.fetchall():
            issues.append({
                'key': row[0],
                'title': row[1],
                'status': row[2],
                'priority': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'labels': row[5] or [],
                'assignee_agent': row[6]
            })
        
        return jsonify({'ok': True, 'issues': issues})


@app.route('/api/issues/<key>')
def api_issue_detail(key):
    """Get single issue with events"""
    with get_db().cursor() as cur:
        # Get issue
        cur.execute("""
            SELECT key, title, description, status, priority,
                   assignee_agent, reporter, created_at, updated_at,
                   labels, metadata
            FROM issues WHERE key = %s
        """, (key,))
        
        row = cur.fetchone()
        if not row:
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        
        issue = {
            'key': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'priority': row[4],
            'assignee_agent': row[5],
            'reporter': row[6],
            'created_at': row[7].isoformat() if row[7] else None,
            'updated_at': row[8].isoformat() if row[8] else None,
            'labels': row[9] or [],
            'metadata': row[10] or {}
        }
        
        # Get events
        cur.execute("""
            SELECT event_type, content, created_at
            FROM issue_events
            WHERE issue_key = %s
            ORDER BY created_at DESC
        """, (key,))
        
        events = []
        for row in cur.fetchall():
            events.append({
                'type': row[0],
                'content': row[1],
                'created_at': row[2].isoformat() if row[2] else None
            })
        
        issue['events'] = events
        return jsonify({'ok': True, 'issue': issue})


@app.route('/api/issues/<key>/update', methods=['POST'])
def api_update_issue(key):
    """Update issue fields"""
    data = request.get_json()
    
    valid_fields = {'status', 'priority', 'title', 'assignee_agent', 'labels'}
    updates = {}
    for field in valid_fields:
        if field in data:
            updates[field] = data[field]
    
    if not updates:
        return jsonify({'ok': False, 'error': 'No valid fields to update'}), 400
    
    with get_db().cursor() as cur:
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
            INSERT INTO issue_events (issue_key, event_type, content)
            VALUES (%s, %s, %s)
        """, (key, event_type, content))
    
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
            INSERT INTO issue_events (issue_key, event_type, content)
            VALUES (%s, %s, %s)
        """, (key, 'comment', comment))
    
    return jsonify({'ok': True, 'message': 'Comment added'})


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


@app.route('/api/stats')
def stats():
    """Get issue statistics"""
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM issues 
            GROUP BY status
        """)
        
        stats = {row[0]: row[1] for row in cur.fetchall()}
        return jsonify({'ok': True, 'stats': stats})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
