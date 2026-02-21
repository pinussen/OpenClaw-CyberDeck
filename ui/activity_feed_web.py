"""
Activity Feed for web display.
Shows recent activities with colored type indicators.
Web-compatible version with HTML rendering.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

try:
    from .cyberpunk_theme_web import COLORS, CyberpunkTheme
except ImportError:
    from cyberpunk_theme_web import COLORS, CyberpunkTheme


@dataclass
class ActivityEntry:
    """Single activity entry in the feed."""
    timestamp: datetime
    type: str       # tool, message, status, error, notification
    title: str
    detail: str = ""
    status: str = "done"  # done, running, fail

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "title": self.title,
            "detail": self.detail,
            "status": self.status,
            "time_str": self.timestamp.strftime("%H:%M")
        }


# Type to color mapping (CSS color names)
TYPE_COLORS_CSS = {
    "tool": "#00f5d4",           # Cyan
    "message": "#ff6b9d",        # Hot pink
    "status": "#9d4edd",         # Electric purple
    "error": "#ff3864",          # Neon red
    "notification": "#ff9e00",   # Amber
}

# Status to color mapping
STATUS_COLORS_CSS = {
    "done": "#00f5d4",      # Neon green/cyan
    "running": "#ff9e00", # Amber
    "fail": "#ff3864",      # Neon red
}


class ActivityFeed:
    """
    Activity feed for web display.
    Shows recent activities with type-coded color bars.
    """

    def __init__(self, theme: CyberpunkTheme = None):
        """
        Initialize the activity feed.

        Args:
            theme: CyberpunkTheme instance (creates one if not provided)
        """
        self.theme = theme or CyberpunkTheme()
        self.entries: List[ActivityEntry] = []
        self._max_entries = 50  # Keep more for web scrolling

    def add_entry(self, type_: str, title: str, detail: str = "", status: str = "done"):
        """Add a new activity entry."""
        entry = ActivityEntry(
            timestamp=datetime.now(),
            type=type_,
            title=title,
            detail=detail,
            status=status,
        )
        self.entries.append(entry)

        # Trim old entries
        if len(self.entries) > self._max_entries:
            self.entries = self.entries[-self._max_entries:]

    def update_latest_status(self, status: str):
        """Update the status of the most recent entry."""
        if self.entries:
            self.entries[-1].status = status

    def clear(self):
        """Clear all entries."""
        self.entries = []

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent entries as list of dicts for JSON."""
        recent = list(reversed(self.entries[-limit:]))
        return [e.to_dict() for e in recent]

    # ============ WEB RENDERING ============
    
    def render_html(self, limit: int = 10) -> str:
        """Render activity feed as HTML."""
        if not self.entries:
            return '<div class="activity-placeholder">No activity yet...</div>'
        
        recent = list(reversed(self.entries[-limit:]))
        
        html_parts = []
        for entry in recent:
            html_parts.append(self._render_entry_html(entry))
        
        return '\n'.join(html_parts)
    
    def _render_entry_html(self, entry: ActivityEntry) -> str:
        """Render a single entry as HTML."""
        bar_color = TYPE_COLORS_CSS.get(entry.type, "#00f5d4")
        status_color = STATUS_COLORS_CSS.get(entry.status, "#666")
        time_str = entry.timestamp.strftime("%H:%M")
        
        # Truncate detail if too long
        detail = entry.detail[:100] + "..." if len(entry.detail) > 100 else entry.detail
        
        html = f'''<div class="activity-item {entry.type}">
    <div class="activity-bar" style="background-color: {bar_color};"></div>
    <div class="activity-content">
        <div class="activity-header-row">
            <span class="activity-title">{self._escape_html(entry.title)}</span>
            <span class="activity-time">{time_str}</span>
        </div>
        {"" if not detail else f'<div class="activity-detail">{self._escape_html(detail)}</div>'}
    </div>
    <div class="activity-status" style="background-color: {status_color};"></div>
</div>'''
        return html.strip()
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML entities."""
        if not text:
            return ""
        return (text
            .replace("\u0026", "\u0026amp;")
            .replace("\u003c", "\u0026lt;")
            .replace("\u003e", "\u0026gt;")
            .replace('"', "\u0026quot;")
        )
    
    def get_json(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get entries as JSON-serializable list."""
        return self.get_recent(limit)
