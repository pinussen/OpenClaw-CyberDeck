#!/usr/bin/env python3
"""Add missing routes to web_server_fixed.py"""

routes_to_add = '''
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
            LIMIT 10
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
        
        stats = dict(cur.fetchall())
        
        return jsonify({
            'ok': True,
            'open_count': open_count,
            'recent_issues': recent,
            'stats': stats
        })

@app.route('/api/queue')
def api_queue():
    """Get queue statistics from issues"""
    with get_db().cursor() as cur:
        # Status counts
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM issues 
            GROUP BY status
        """)
        queue = dict(cur.fetchall())
        
        # Recent issues
        cur.execute("""
            SELECT key, title, status, priority
            FROM issues 
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        recent = []
        for row in cur.fetchall():
            recent.append({
                'key': row[0],
                'title': row[1],
                'status': row[2],
                'priority': row[3]
            })
        
        return jsonify({
            'ok': True,
            'queue': queue,
            'recent': recent
        })

'''

with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server_fixed.py', 'r') as f:
    content = f.read()

if '@app.route(\'/api/dashboard/summary\')' not in content:
    content = routes_to_add + content
    with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server_fixed.py', 'w') as f:
        f.write(content)
    print('✅ Added missing routes to web_server_fixed.py')
else:
    print('Routes already exist')
