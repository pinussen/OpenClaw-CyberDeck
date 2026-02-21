"""
Status Display for web - outputs JSON for web command panel.
"""

import threading
from datetime import datetime
from typing import Dict, Any, Optional

from websocket_client import ConnectionState


class StatusDisplayWeb:
    """
    Manages status display for web output.
    Outputs JSON instead of rendering to SPI display.
    """
    
    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode
        self.lock = threading.Lock()
        
        # Status data
        self._connected = False
        self._connection_state = ConnectionState.DISCONNECTED
        self._task_summary = "Initializing..."
        self._queue_count = 0
        self._api_cost = 0.0
        self._tokens_in = 0
        self._tokens_out = 0
        self._model = "unknown"
        self._is_streaming = False
        self._last_activity = datetime.now()
        
    def initialize(self):
        """Initialize (no hardware needed for web)."""
        print("[StatusDisplayWeb] Initialized")
        return True
    
    def shutdown(self):
        """Shutdown."""
        pass
    
    def update_connection(self, connected: bool, state: ConnectionState):
        """Update connection status."""
        with self.lock:
            self._connected = connected
            self._connection_state = state
            self._last_activity = datetime.now()
    
    def update_task(self, summary: str):
        """Update current task."""
        with self.lock:
            self._task_summary = summary
            self._last_activity = datetime.now()
    
    def update_queue(self, count: int):
        """Update queue count."""
        with self.lock:
            self._queue_count = count
    
    def update_usage(self, cost: float, tokens_in: int, tokens_out: int):
        """Update API usage."""
        with self.lock:
            self._api_cost = cost
            self._tokens_in = tokens_in
            self._tokens_out = tokens_out
    
    def update_model(self, model: str):
        """Update model name."""
        with self.lock:
            self._model = model
    
    def set_streaming(self, is_streaming: bool):
        """Set streaming state."""
        with self.lock:
            self._is_streaming = is_streaming
    
    # ============ WEB OUTPUT ============
    
    def get_json(self) -> Dict[str, Any]:
        """Get status as JSON-serializable dict."""
        with self.lock:
            return {
                "connected": self._connected,
                "connection_state": self._connection_state.value,
                "task_summary": self._task_summary,
                "queue_count": self._queue_count,
                "api_cost": round(self._api_cost, 4),
                "tokens_in": self._tokens_in,
                "tokens_out": self._tokens_out,
                "model": self._model,
                "is_streaming": self._is_streaming,
                "last_activity": self._last_activity.isoformat(),
                "demo_mode": self.demo_mode,
                "timestamp": datetime.now().isoformat()
            }
    
    def render_html(self) -> str:
        """Render status panel as HTML."""
        status = self.get_json()
        
        state_color = "#00f5d4" if status["connected"] else "#ff3864"
        state_text = "Connected" if status["connected"] else "Disconnected"
        
        html = f'''<div class="status-panel">
    <div class="status-row">
        <span class="status-label">Connection:</span>
        <span class="status-value" style="color: {state_color};">{state_text}</span>
    </div>
    <div class="status-row">
        <span class="status-label">Task:</span>
        <span class="status-value">{status["task_summary"]}</span>
    </div>
    <div class="status-row">
        <span class="status-label">Queue:</span>
        <span class="status-value">{status["queue_count"]}</span>
    </div>
    <div class="status-row">
        <span class="status-label">Cost:</span>
        <span class="status-value">${status["api_cost"]:.4f}</span>
    </div>
    <div class="status-row">
        <span class="status-label">Model:</span>
        <span class="status-value">{status["model"]}</span>
    </div>
</div>'''
        return html.strip()
