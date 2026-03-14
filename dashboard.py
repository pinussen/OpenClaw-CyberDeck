#!/usr/bin/env python3
"""
CyberDeck Dashboard - Issues overview for main cyberdeck UI
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify
from lib.database import get_db

app = Flask(__name__)


@app.route('/api/dashboard/summary')
def dashboard_summary():
    """Get dashboard summary for cyberdeck"""
    with get_db().cursor() as cur:
        # Get open issues count
        cur.execute("""
            SELECT COUNT(*) FROM issues 
            WHERE status IN ('todo', 'in_progress', 'blocked')
        """)
        open_count = cur.fetchone()[0]
        
        # Get recent open issues with assignee info
        cur.execute("""
            SELECT key, title, status, priority, labels, assignee_agent
            FROM issues 
            WHERE status IN ('todo', 'in_progress', 'blocked')
            ORDER BY created_at DESC
            LIMIT 5
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
                'has_labels': bool(row[4])
            })
        
        # Get stats by status
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM issues 
            WHERE status IN ('todo', 'in_progress', 'blocked', 'done')
            GROUP BY status
        """)
        
        stats = {}
        for row in cur.fetchall():
            stats[row[0]] = row[1]
        
        return jsonify({
            'ok': True,
            'open_count': open_count,
            'recent_issues': recent,
            'stats': stats
        })


@app.route('/api/dashboard/issues')
def dashboard_issues():
    """Get all open issues"""
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT key, title, status, priority, labels, assignee_agent
            FROM issues 
            WHERE status IN ('todo', 'in_progress', 'blocked')
            ORDER BY 
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END
        """)
        
        issues = []
        for row in cur.fetchall():
            issues.append({
                'key': row[0],
                'title': row[1],
                'status': row[2],
                'priority': row[3],
                'labels': row[4] or [],
                'assignee': row[5]
            })
        
        return jsonify({'ok': True, 'issues': issues})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
