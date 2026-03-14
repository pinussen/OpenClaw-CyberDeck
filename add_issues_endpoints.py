#!/usr/bin/env python3
"""Add issues endpoints to web_server.py"""

import sys

# Read the file
with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server.py', 'r') as f:
    content = f.read()

# Find where to insert (after queue endpoint)
insert_marker = '@app.route(\'/api/queue\')'
if insert_marker not in content:
    print("Could not find insertion point")
    sys.exit(1)

# Find end of queue endpoint (next @app.route or def)
lines = content.split('\n')
insert_pos = None
for i, line in enumerate(lines):
    if '@app.route(\'/api/queue\')' in line:
        # Find the end of this route (next @app.route or def at start of line)
        for j in range(i+1, len(lines)):
            if lines[j].startswith('@app.route(') or (lines[j].startswith('def ') and not lines[j].startswith('        def ')):
                insert_pos = j
                break
        break

if insert_pos is None:
    print("Could not find insertion point")
    sys.exit(1)

# New routes to insert
new_routes = '''
@app.route('/issues')
def issues_view():
    """Render issues list page."""
    if not ISSUES_VIEW_AVAILABLE:
        return '<h1>❌ Issues view not available</h1><p>Please ensure PostgreSQL is running.</p>', 500
    return render_template('issues.html')

@app.route('/api/issues')
def api_issues():
    """Get list of issues with filters."""
    if not ISSUES_VIEW_AVAILABLE:
        return jsonify({'ok': False, 'error': 'Issues view not available'}), 500
    
    view = IssuesView()
    
    # Get filters
    status = request.args.get('status')
    priority = request.args.get('priority')
    limit = int(request.args.get('limit', 50))
    
    # Get issues
    issues = view.list_issues(status=status, limit=limit)
    
    # Filter by priority if specified
    if priority:
        issues = [i for i in issues if i.get('priority') == priority]
    
    # Get stats
    stats = view.get_statistics()
    
    return jsonify({
        'ok': True,
        'issues': issues,
        'stats': stats,
        'count': len(issues)
    })

@app.route('/api/issues/<key>')
def api_issue_detail(key):
    """Get single issue details."""
    if not ISSUES_VIEW_AVAILABLE:
        return jsonify({'ok': False, 'error': 'Issues view not available'}), 500
    
    view = IssuesView()
    issue = view.get_issue(key)
    
    if not issue:
        return jsonify({'ok': False, 'error': f'Issue {key} not found'}), 404
    
    # Get recent activity for this issue
    events = view.get_recent_activity(limit=10)
    
    return jsonify({
        'ok': True,
        'issue': issue,
        'recent_activity': events
    })

'''

# Insert the new routes
lines.insert(insert_pos, new_routes)

# Write back
with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/web_server.py', 'w') as f:
    f.write('\n'.join(lines))

print("✅ Issues endpoints added to web_server.py")
print(f"   Inserted at line {insert_pos}")
