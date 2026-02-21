"""
Display Main - Web-compatible version
Conversation display with Molty and activity feed for web interface.
"""

import threading
import time
from datetime import datetime
from typing import Optional, Callable, Dict, List, Any

# Import UI components (web versions)
from ui.activity_feed_web import ActivityFeed
from ui.molty_web import Molty, MoltyState
from ui.cyberpunk_theme_web import CyberpunkTheme


class ConversationDisplay:
    """
    Manages the conversation view with Molty character and activity feed.
    Web-compatible version - outputs HTML/SVG/JSON instead of PIL images.
    """

    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode
        self.lock = threading.Lock()
        self.running = False
        
        # Cyberpunk UI components
        self.theme = CyberpunkTheme()
        self.molty = Molty()
        self.activity_feed = ActivityFeed(theme=self.theme)
        
        # State
        self._status_text = "Waiting for commands..."
        self._is_streaming = False
        self._streaming_content = ""
        self._messages = []
        
        # Callbacks for bridge
        self._on_activity_added: Optional[Callable] = None

    def initialize(self):
        """Initialize (no hardware needed for web)."""
        self.running = True
        print("[ConversationDisplay] Web mode initialized")
        return True

    def shutdown(self):
        """Shutdown."""
        self.running = False

    def add_activity(self, activity_type: str, title: str, detail: str = "", status: str = "done"):
        """Add activity to feed."""
        with self.lock:
            self.activity_feed.add_entry(activity_type, title, detail, status)
            
            # Update Molty state based on activity
            if activity_type == "tool":
                self.set_molty_state(MoltyState.WORKING)
            elif activity_type == "error":
                self.set_molty_state(MoltyState.ERROR)
            elif status == "done":
                self.set_molty_state(MoltyState.SUCCESS)
            
            # Trigger callback for real-time updates
            if self._on_activity_added:
                try:
                    self._on_activity_added()
                except Exception as e:
                    print(f"[ConversationDisplay] Activity callback error: {e}")

    def add_message(self, role: str, content: str):
        """Add a message."""
        with self.lock:
            self._messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self.activity_feed.add_entry(
                "message",
                role.capitalize(),
                content[:100],
                "done"
            )

    def set_streaming(self, is_streaming: bool, content: str = ""):
        """Set streaming state."""
        with self.lock:
            self._is_streaming = is_streaming
            self._streaming_content = content
            if is_streaming:
                self.set_molty_state(MoltyState.WORKING)

    def set_molty_state(self, state: MoltyState, duration: float = 0):
        """Set Molty animation state."""
        self.molty.set_state(state)

    def set_status(self, text: str):
        """Set status text."""
        self._status_text = text

    def set_activity_callback(self, callback: Callable):
        """Set callback when activity is added."""
        self._on_activity_added = callback

    def clear(self):
        """Clear all data."""
        with self.lock:
            self.activity_feed.clear()
            self._messages.clear()
            self._streaming_content = ""
            self._is_streaming = False

    # ============ WEB OUTPUT METHODS ============
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary for JSON API."""
        with self.lock:
            return {
                "molty_state": self.molty.get_state(),
                "status_text": self._status_text,
                "is_streaming": self._is_streaming,
                "streaming_content": self._streaming_content if self._is_streaming else "",
                "activities": self.activity_feed.get_recent(limit=20),
                "messages": self._messages[-10:],  # Last 10 messages
                "timestamp": datetime.now().isoformat()
            }
    
    def render_html_molty(self) -> str:
        """Render Molty as SVG."""
        return self.molty.render_svg()
    
    def render_html_activities(self, limit: int = 10) -> str:
        """Render activity feed as HTML."""
        return self.activity_feed.render_html(limit=limit)
    
    def get_molty_state_info(self) -> Dict[str, Any]:
        """Get Molty state info for UI."""
        return self.molty.get_state_info()
    
    def get_activities_json(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get activities as list of dicts."""
        return self.activity_feed.get_recent(limit=limit)
