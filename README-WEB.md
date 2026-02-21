# OpenClaw CyberDeck - Web Version for PinePhone

A web-based interface for the CyberDeck, optimized for PinePhone touchscreen.

## Quick Start

```bash
cd ~/.openclaw/workspace-dev/cyberdeck
./run-web.sh
```

Then access on PinePhone: `http://<r630-ip>:5000`

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements-web.txt
```

2. Configuration (optional):
```bash
cp .env.example .env
# Edit .env with your OpenClaw settings
```

3. Run the server:
```bash
python3 web_server.py --demo    # Demo mode (no OpenClaw connection)
python3 web_server.py           # Live mode
```

## Features

- **Real-time updates**: WebSocket connection for live activity feed
- **Molty mascot**: Animated space lobster with state-based animations
- **Activity feed**: Shows OpenClaw events (tool calls, messages, status)
- **Touch optimized**: Large buttons, swipe-friendly design for PinePhone
- **Cyberpunk theme**: Neon colors, glowing effects

## Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   PinePhone     │ ◄────────────────► │   Flask Server  │
│   (Browser)     │                     │   (Port 5000)   │
└─────────────────┘                     └────────┬────────┘
                                                 │
                                            OpenClaw
                                            WebSocket
                                                 │
                                         ┌───────▼────────┐
                                         │ OpenClaw       │
                                         │ Gateway        │
                                         └────────────────┘
```

## Files

| File | Description |
|------|-------------|
| `web_server.py` | Flask + SocketIO server |
| `display_main_web.py` | Conversation display (web output) |
| `display_status_web.py` | Status panel (JSON output) |
| `ui/molty_web.py` | Animated mascot with SVG output |
| `ui/activity_feed_web.py` | Activity feed (HTML output) |
| `templates/cyberdeck.html` | PinePhone UI |
| `static/css/cyberdeck.css` | Cyberpunk theme styles |

## API Endpoints

- `GET /api/status` - Current connection status
- `GET /api/display-state` - Full display state (activities, Molty state)
- `POST /api/command` - Execute commands (status, clear, demo)

## WebSocket Events

**Server → Client:**
- `activity` - New activity notification
- `status` - Status update
- `message` - Message events
- `display_state` - Full state update

**Client → Server:**
- `command` - Send command
- `ping` - Keepalive

## PinePhone Setup

1. Connect PinePhone to same network as R630
2. Open browser and navigate to `http://<r630-ip>:5000`
3. For fullscreen: Add to home screen or use browser fullscreen mode

## Development

Run in demo mode for testing without OpenClaw:
```bash
python3 web_server.py --demo
```

This generates fake activity data for testing the UI.

## Original Hardware Version

See original README.md for Raspberry Pi 4 + SPI display setup.
