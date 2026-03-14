#!/usr/bin/env python3
"""Track what Main agent is working on for display in CyberDeck Queue panel."""

import json
import time
from datetime import datetime
from pathlib import Path

STATUS_FILE = Path("/home/bjwl/.openclaw/workspace-dev/cyberdeck/main_status.json")

def update_status(task: str, category: str = "working"):
    """Update Main's current task."""
    STATUS_FILE.write_text(json.dumps({
        "agent": "main",
        "task": task,
        "category": category,
        "since": datetime.now().isoformat(),
        "timestamp": time.time()
    }, indent=2))

def clear_status():
    """Mark Main as idle."""
    STATUS_FILE.write_text(json.dumps({
        "agent": "main", 
        "task": "Idle",
        "category": "idle",
        "since": datetime.now().isoformat(),
        "timestamp": time.time()
    }, indent=2))

def get_status():
    """Get Main's current status."""
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {"agent": "main", "task": "Unknown", "category": "unknown"}

def get_current_task_summary():
    """Get a short summary of what Main is working on for display."""
    status = get_status()
    task = status.get('task', 'Idle')
    category = status.get('category', 'idle')
    
    # Truncate if too long
    if len(task) > 35:
        task = task[:32] + '...'
    
    return {
        'id': 'main',
        'task': task,
        'category': category,
        'since': status.get('since', '')
    }

if __name__ == "__main__":
    # Test
    update_status("Testing CyberDeck UI")
    print(get_status())
