"""
Cyberpunk Theme - Web-compatible (no PIL)
Color definitions and theme utilities for web rendering.
"""


# Color definitions (RGB tuples for compatibility with original)
COLORS = {
    # Backgrounds
    "bg_primary": (10, 10, 15),      # Main background
    "bg_secondary": (18, 18, 26),    # Panel backgrounds
    "bg_tertiary": (26, 26, 36),     # Elevated surfaces
    
    # Borders
    "border": (42, 42, 58),          # Subtle borders
    "panel_border": (58, 58, 74),    # Panel borders
    "panel_bg": (20, 20, 28),        # Activity feed bg
    
    # Neon Accents
    "neon_cyan": (0, 245, 212),      # Primary accent
    "neon_green": (0, 217, 255),     # Success
    "neon_red": (255, 56, 100),      # Error
    "hot_pink": (255, 107, 157),     # Secondary accent
    "electric_purple": (157, 78, 221), # Tertiary accent
    "amber": (255, 158, 0),          # Warning/active
    
    # Text
    "text_primary": (224, 224, 224),   # Main text
    "text_secondary": (160, 160, 160), # Secondary text
    "text_dim": (96, 96, 96),        # Muted text
    "text_disabled": (64, 64, 64),   # Disabled text
    
    # Type indicators
    "type_tool": (0, 245, 212),      # Cyan - Tool calls
    "type_message": (255, 107, 157), # Pink - User/assistant messages
    "type_status": (157, 78, 221),   # Purple - Status updates
    "type_error": (255, 56, 100),    # Red - Errors
    "type_notification": (255, 158, 0), # Amber - Notifications
}


# CSS color mapping (for web)
COLLORS_CSS = {k: f"rgb{v}" for k, v in COLORS.items()}


class CyberpunkTheme:
    """Cyberpunk theme for web rendering."""
    
    def __init__(self):
        """Initialize theme."""
        self.colors = COLORS
    
    def get_color(self, name: str) -> tuple:
        """Get color by name (returns RGB tuple)."""
        return self.colors.get(name, (128, 128, 128))
    
    def get_color_css(self, name: str) -> str:
        """Get color as CSS rgb() string."""
        rgb = self.get_color(name)
        return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
    
    def get_color_hex(self, name: str) -> str:
        """Get color as hex string."""
        rgb = self.get_color(name)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def to_css_variables(self) -> str:
        """Export colors as CSS variables."""
        css_lines = ["<style>:root {"]
        for name, rgb in self.colors.items():
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            var_name = name.replace("_", "-")
            css_lines.append(f"  --{var_name}: {hex_color};")
        css_lines.append("}</style>")
        return "\n".join(css_lines)
