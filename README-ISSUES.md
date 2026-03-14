# CyberDeck Web UI - Issues Integration

## ✅ What's Done

### 1. Issues Manager (/issues)
Full CRUD interface for native issues:
- **View** all issues with filters (status, priority)
- **Open** individual issues to see details
- **Update** status, priority, assignee
- **Add comments** to issues
- **Create** new issues
- **See** event history for each issue

### 2. Dashboard (/dashboard)
Quick overview page showing:
- Count of open issues
- Recent open issues with assignee info
- Quick links to full issue manager

### 3. Main UI (/)
CyberDeck dashboard with:
- Activity feed
- Queue statistics (from issues DB)
- Recent issues list
- Quick links to issues manager and dashboard
- Message input (sends to Telegram)

### 4. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/issues` | GET | List issues with filters |
| `/api/issues/<key>` | GET | Get single issue with events |
| `/api/issues/<key>/update` | POST | Update issue fields |
| `/api/issues/<key>/comment` | POST | Add comment to issue |
| `/api/issues/create` | POST | Create new issue |
| `/api/queue` | GET | Queue statistics and recent issues |
| `/api/activities` | GET | Activity feed |
| `/api/dashboard/summary` | GET | Dashboard summary data |

## 🚀 Quick Start

```bash
cd ~/.openclaw/workspace-dev/cyberdeck
source .venv/bin/activate

# Start server on port 5000
python3 web_server_fixed.py --live

# Or use the helper script
./start.sh
```

Then open in browser: `http://localhost:5000`

## 📁 Files Created

### Backend
- `web_server_fixed.py` - Main web server with all endpoints
- `issues_full.py` - Standalone issues viewer (optional)
- `dashboard.py` - Dashboard data API (optional)
- `issues_view.py` - PostgreSQL issues data access

### Frontend Templates
- `templates/cyberdeck.html` - Main UI
- `templates/issues_full.html` - Issues manager
- `templates/dashboard.html` - Issues dashboard

## 🎨 UI Features

### Main Dashboard
- Real-time activity feed
- Queue statistics panel
- Recent issues sidebar
- Message input box
- Connection status indicator

### Issues Manager
- Grid view of all issues
- Filter by status/priority
- Modal detail view
- Inline editing (status, priority, assignee)
- Comment section
- Event history timeline
- Create new issue modal

### Dashboard
- Open issues count
- Recent open issues list
- Quick navigation links
- Clean, cyberpunk aesthetic

## 🔧 Technical Details

- Flask + SocketIO for real-time updates
- PostgreSQL for issue storage
- No external dependencies (uses existing venv)
- Touch-optimized for PinePhone/CyberDeck
- Responsive design (mobile-friendly)

## 🐛 Known Issues to Fix

1. WebSocket connection - needs OpenClaw Gateway integration
2. Real-time activity feed - currently static
3. Agent status - needs agent discovery
4. Queue monitoring - works with issues DB now

## 📝 Next Steps

1. Fix WebSocket connection to OpenClaw Gateway
2. Add agent discovery
3. Enable real-time activity updates
4. Add more filters to issues manager
5. Add issue cloning/duplicate feature
6. Add bulk operations (close multiple, etc.)

## 🎯 GOR-61 Example

Your pump sensor issue is already in the system:
- **GOR-61**: "Sensor för pumpkontroll i borrhål - ofta start/stopp"
- Status: todo
- Priority: medium
- Labels: sensor, pump, borrahall, vatten

You can view it at `/issues` or directly at `/api/issues/GOR-61`
