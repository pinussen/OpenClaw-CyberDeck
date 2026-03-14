#!/usr/bin/env python3
"""
Native Issues View - Display issues from PostgreSQL issue system
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.database import get_db


class IssuesView:
    """View for native issue system."""
    
    def __init__(self):
        self.db = get_db()
    
    def list_issues(self, status=None, labels=None, assignee=None, limit=50):
        """List issues with filters."""
        with self.db.cursor() as cur:
            query = """
                SELECT 
                    key, title, description, status, priority,
                    assignee_agent, reporter, created_at, updated_at,
                    labels, metadata
                FROM issues
                WHERE 1=1
            """
            params = []
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            if labels:
                query += " AND %s::text[] && labels"
                params.append(labels)
            
            if assignee:
                query += " AND assignee_agent = %s"
                params.append(assignee)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            
            issues = []
            for row in cur.fetchall():
                issues.append({
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
                })
            
            return issues
    
    def get_issue(self, key):
        """Get single issue by key."""
        with self.db.cursor() as cur:
            cur.execute("""
                SELECT 
                    key, title, description, status, priority,
                    assignee_agent, reporter, created_at, updated_at,
                    labels, metadata
                FROM issues
                WHERE key = %s
            """, (key,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
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
    
    def get_statistics(self):
        """Get issue statistics by status."""
        with self.db.cursor() as cur:
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM issues
                GROUP BY status
                ORDER BY 
                    CASE status
                        WHEN 'todo' THEN 1
                        WHEN 'in_progress' THEN 2
                        WHEN 'blocked' THEN 3
                        WHEN 'review' THEN 4
                        WHEN 'done' THEN 5
                        WHEN 'cancelled' THEN 6
                        WHEN 'onhold' THEN 7
                        WHEN 'waiting' THEN 8
                        ELSE 9
                    END
            """)
            
            stats = {}
            for row in cur.fetchall():
                stats[row[0]] = row[1]
            
            return stats
    
    def get_recent_activity(self, limit=20):
        """Get recent issue events."""
        with self.db.cursor() as cur:
            cur.execute("""
                SELECT 
                    ie.event_type, ie.content, ie.created_at,
                    i.key, i.title, i.status
                FROM issue_events ie
                JOIN issues i ON ie.issue_key = i.key
                ORDER BY ie.created_at DESC
                LIMIT %s
            """, (limit,))
            
            events = []
            for row in cur.fetchall():
                events.append({
                    'event_type': row[0],
                    'content': row[1],
                    'created_at': row[2].isoformat() if row[2] else None,
                    'issue_key': row[3],
                    'issue_title': row[4],
                    'issue_status': row[5]
                })
            
            return events


if __name__ == '__main__':
    view = IssuesView()
    
    print("=== Issue Statistics ===")
    stats = view.get_statistics()
    for status, count in stats.items():
        print(f"  {status}: {count}")
    
    print("\n=== Recent Issues ===")
    issues = view.list_issues(limit=10)
    for issue in issues:
        print(f"{issue['key']}: {issue['title']} [{issue['status']}]")
    
    print("\n=== Recent Activity ===")
    events = view.get_recent_activity(5)
    for event in events:
        print(f"{event['issue_key']}: {event['event_type']} - {event['content'][:50]}...")
