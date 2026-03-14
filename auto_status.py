#!/usr/bin/env python3
"""Auto-update Main agent status based on activity."""

import time
import threading
from datetime import datetime, timedelta
from main_status import update_status, clear_status

class AutoStatus:
    def __init__(self, idle_timeout=120):  # 2 minuter
        self.idle_timeout = idle_timeout
        self.last_activity = time.time()
        self.current_task = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the auto-status monitor."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the monitor."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def activity(self, task_description):
        """Call this when starting a new task."""
        with self.lock:
            self.last_activity = time.time()
            self.current_task = task_description
            update_status(task_description)
    
    def done(self):
        """Call this when task is complete."""
        with self.lock:
            self.last_activity = time.time()
            self.current_task = None
            clear_status()
    
    def _monitor(self):
        """Background thread that clears status after idle timeout."""
        while self.running:
            time.sleep(10)  # Check every 10 seconds
            
            with self.lock:
                idle_time = time.time() - self.last_activity
                
                if idle_time > self.idle_timeout and self.current_task:
                    # Auto-clear after timeout
                    self.current_task = None
                    clear_status()

# Global instance
_auto_status = None

def init_auto_status(idle_timeout=120):
    """Initialize the auto-status system."""
    global _auto_status
    if _auto_status is None:
        _auto_status = AutoStatus(idle_timeout)
        _auto_status.start()
    return _auto_status

def set_working(task):
    """Set current working task."""
    if _auto_status:
        _auto_status.activity(task)

def set_done():
    """Mark task as done."""
    if _auto_status:
        _auto_status.done()

if __name__ == '__main__':
    # Test
    init_auto_status(idle_timeout=10)  # 10 seconds for testing
    set_working("Testing auto-status")
    print("Status set to working, waiting 15 seconds...")
    time.sleep(15)
    print("Should be cleared now")
