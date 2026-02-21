"""
Cyberpunk UI module for OpenClaw CyberDeck Web.
Web-compatible versions without PIL dependencies.
"""

# Only export web-compatible modules
try:
    from .cyberpunk_theme_web import CyberpunkTheme, COLORS as CYBERPUNK_COLORS
    from .molty_web import Molty, MoltyState
    from .activity_feed_web import ActivityFeed, ActivityEntry
except ImportError as e:
    print(f"[UI] Warning: Could not import web UI modules: {e}")
    # Fallback empty imports
    CyberpunkTheme = None
    CYBERPUNK_COLORS = {}
    Molty = None
    MoltyState = None
    ActivityFeed = None
    ActivityEntry = None

__all__ = [
    'CyberpunkTheme',
    'CYBERPUNK_COLORS',
    'Molty',
    'MoltyState',
    'ActivityFeed',
    'ActivityEntry',
]
