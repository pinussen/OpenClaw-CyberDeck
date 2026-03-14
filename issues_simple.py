#!/usr/bin/env python3
"""
Simple Issues Viewer - Standalone Flask app for native issues
Runs on port 5002, can be accessed alongside CyberDeck
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
from lib.database import get_db

app = Flask(__name__)


@app.route('/')
def issues():
    """Render issues list."""
    return render_template('issues_simple.html')


@app.route('/api/issues')
def api_issues():
    """Get issues from database."""
    with get_db().cursor() as cur:
        status = request.args.get('status')
        
        query = """
            SELECT key, title, status, priority, created_at, labels
            FROM issues
        """
        params = []
        
        if status:
            query += " WHERE status = %s"
            params.append(status)
        
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
                'labels': row[5] or []
            })
        
        return jsonify({'ok': True, 'issues': issues})


@app.route('/api/stats')
def stats():
    """Get issue statistics."""
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM issues 
            GROUP BY status
        """)
        
        stats = {}
        for row in cur.fetchall():
            stats[row[0]] = row[1]
        
        return jsonify({'ok': True, 'stats': stats})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
