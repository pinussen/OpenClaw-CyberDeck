#!/usr/bin/env python3
"""Add dashboard API to web_server_fixed.py"""

import sys

with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server_fixed.py', 'r') as f:
    content = f.read()

# Find where to insert (after issues routes)
if '@app.route(\'/api/stats\')' in content:
    # Add dashboard routes before stats
    dashboard_routes = '''
@app.route('/api/dashboard/summary')
def dashboard_summary():
    """Get dashboard summary for cyberdeck"""
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM issues 
            WHERE status IN ('todo', 'in_progress', 'blocked')
        """)
        open_count = cur.fetchone()[0]
        
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

'''
    content = content.replace('@app.route(\'/api/stats\')', dashboard_routes + '@app.route(\'/api/stats\')')
    
    with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server_fixed.py', 'w') as f:
        f.write(content)
    print('✅ Dashboard API added to web_server_fixed.py')
else:
    print('Stats route not found - routes may have changed')
