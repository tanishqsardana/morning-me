# Morning Me

A personalized morning planning assistant that integrates your calendar, weather forecasts, and local events to help you start your day right. Built with Open WebUI and powered by custom MCP (Model Context Protocol) servers.

Youtube Link - https://youtu.be/yZxSTWwz3dQ

## 🌟 Features

- **Morning Briefings**: Get a concise daily overview with your schedule, weather, and outfit suggestions
- **Calendar Integration**: Seamlessly manage Google Calendar events through natural language
- **Weather Intelligence**: Real-time weather forecasts with outfit recommendations based on temperature and formality
- **Event Discovery**: Find and explore NYC events based on your interests and location
- **Smart Suggestions**: Proactive recommendations for travel buffers, meal planning, and conflict resolution

## 🛠️ Tech Stack

### Core Technologies
- **Open WebUI**: Web-based interface for AI interactions
- **Python 3.12+**: Backend services and MCP servers
- **TypeScript/Node.js**: Google Calendar MCP server
- **Model Context Protocol (MCP)**: Protocol for AI-tool integration

### MCP Servers

#### 1. NYC Events MCP Server (Custom)
- **Language**: Python
- **Framework**: FastMCP, Starlette, Uvicorn
- **Features**: 
  - Search events by query, category, date range, or location
  - Get event details and categories
  - Proximity-based event discovery
- **Location**: `nyc_events_mcp/`

#### 2. Google Calendar MCP Server (Custom)
- **Language**: TypeScript/Node.js
- **Framework**: Model Context Protocol SDK
- **Features**:
  - Multi-calendar support
  - Event CRUD operations
  - Recurring event management
  - Free/busy queries
  - Smart scheduling
- **Location**: `google-calendar-mcp/`

### Tools & Integrations
- **Weather Tool**: Keyless weather API integration using Open-Meteo
- **Tavily**: Web search and crawling for event discovery
- **Google Calendar API**: Calendar management and event operations

## 📋 Prerequisites

- Python 3.12 or higher
- Node.js (v20+ recommended)
- npm or yarn
- Open WebUI installed
- Google Cloud Project with Calendar API enabled (for Google Calendar MCP)
- OAuth 2.0 credentials for Google Calendar

## 🚀 Setup Instructions

### 1. Start Open WebUI Server

In the `morning_me` folder:

```bash
open-webui serve
```

This starts the Open WebUI interface, typically on `http://localhost:3000` (or as configured).

### 2. Start NYC Events MCP Server

In the `morning_me` folder:

```bash
python -m nyc_events_mcp.server --mode sse --host 0.0.0.0 --port 8022
```

This starts the NYC Events MCP server in SSE (Server-Sent Events) mode on port 8022.

### 3. Start MCP Connector for NYC Events

In the `nyc_events_mcp` folder:

```bash
uvx mcpo --port 8023 --server-type sse -- http://127.0.0.1:8022/sse
```

This runs the MCP connector proxy for the NYC Events server on port 8023.

### 4. Start Google Calendar MCP Server

In the `google_calendar_mcp` folder:

```bash
mcpo --port 8000 -- node build/index.js
```

This starts the Google Calendar MCP server on port 8000.

**Note**: Make sure you've built the Google Calendar MCP server first:
```bash
cd google-calendar-mcp
npm install
npm run build
```

## 📁 Project Structure

```
morning_me/
├── google-calendar-mcp/      # Google Calendar MCP server (TypeScript)
│   ├── src/                   # Source code
│   ├── build/                 # Compiled JavaScript
│   └── package.json           # Node.js dependencies
├── nyc_events_mcp/            # NYC Events MCP server (Python)
│   ├── src/                   # Source code
│   │   └── nyc_events_mcp/
│   │       ├── server.py      # Main server implementation
│   │       └── tools/         # Tool handlers
│   └── requirements.txt       # Python dependencies
├── weather_tool.py            # Weather integration tool
├── modelparams_systemprompt.txt  # System prompt configuration
├── prompt_suggestions.txt     # Quick prompt templates
└── README.md                  # This file
```

## 🔧 Configuration

### Google Calendar MCP Setup

1. Create a Google Cloud project and enable the Calendar API
2. Create OAuth 2.0 credentials (Desktop app type)
3. Save credentials to `google-calendar-mcp/gcp-oauth.keys.json`
4. On first run, complete the OAuth flow in your browser

### NYC Events MCP Setup

The NYC Events MCP server uses CSV data for events. Ensure your event data file is properly formatted and accessible.

### Open WebUI Configuration

Configure Open WebUI to connect to your MCP servers. The configuration typically includes:
- MCP server endpoints
- API keys (if required)
- User preferences (stored in `prefs.json`)

## 💡 Usage Examples

### Morning Brief
```
Morning brief for {{CURRENT_DATE}} ({{CURRENT_TIME}} {{CURRENT_TIMEZONE}}). Use my saved preferences.
```

### Create Calendar Event
```
Create "{{title}}" on {{date}} at {{time}} ({{duration}}) at "{{location}}". Ask before adding.
```

### Weather + Outfit Suggestion
```
Today's weather in my saved city + one outfit matching my dress_code and first event's formality.
```

## 🎯 Key Features Explained

### Morning Brief Procedure
When requested, Morning Me:
1. Fetches today's events from Google Calendar
2. Gets weather forecast for your city
3. Provides:
   - **Today at a glance**: Chronological schedule with conflicts flagged
   - **Outfit**: Weather-based recommendations considering event formality
   - **Food**: Meal suggestions aligned with your diet and schedule
   - **Moves**: Proactive suggestions (travel buffers, conflict resolution)

### Smart Outfit Recommendations
- Temperature-based clothing suggestions
- Formality adjustments based on event context
- Weather-aware (rain/snow protection)
- Location-aware suggestions

### Event Discovery
- Search NYC events by category, date, or location
- Proximity-based discovery
- Integration with major event platforms (Eventbrite, Meetup, Dice.fm)

## 🔌 MCP Server Details

### NYC Events MCP Server

**Available Tools**:
- `get_event_categories`: List all event categories
- `search_events`: Search events by query string
- `get_events_by_category`: Filter events by category
- `get_events_by_date_range`: Get events within a date range
- `find_events_near_location`: Discover events near coordinates
- `get_event_by_id`: Get detailed event information

**Transport**: SSE (Server-Sent Events) or stdio

### Google Calendar MCP Server

**Available Tools**:
- Calendar listing and management
- Event CRUD operations
- Recurring event handling
- Free/busy queries
- Conflict detection
- Smart scheduling

**Transport**: stdio or HTTP

## 🐛 Troubleshooting

### Port Conflicts
If ports are already in use, modify the port numbers in the startup commands:
- NYC Events MCP: Change `--port 8022`
- MCP Connector: Change `--port 8023`
- Google Calendar MCP: Change `--port 8000`

### Authentication Issues
- Google Calendar: Ensure OAuth credentials are valid and test user is added
- Check token expiration (test mode tokens expire after 7 days)

### Server Connection Issues
- Verify all servers are running before starting Open WebUI
- Check firewall settings for localhost connections
- Ensure Python and Node.js dependencies are installed

## 📝 Development

### Installing Dependencies

**Python (NYC Events MCP)**:
```bash
cd nyc_events_mcp
pip install -r requirements.txt
```

**Node.js (Google Calendar MCP)**:
```bash
cd google-calendar-mcp
npm install
npm run build
```

### Testing

Test individual MCP servers using MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
```

## 📄 License

See individual component licenses:
- Google Calendar MCP: MIT (see `google-calendar-mcp/LICENSE`)
- NYC Events MCP: Check `nyc_events_mcp/` for license information

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📚 Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Open WebUI Documentation](https://docs.openwebui.com)
- [Google Calendar API Documentation](https://developers.google.com/calendar)

---

**Built with ❤️ for better mornings**
