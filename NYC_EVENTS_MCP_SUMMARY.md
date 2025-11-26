# NYC Events MCP Server - Project Summary

## What Was Built

A complete **Model Context Protocol (MCP) server** that queries your NYC events SQLite database and integrates seamlessly with Claude Desktop and your Google Calendar MCP server.

## 🎯 Key Features

### 1. **Proximity-Based Search** (🌟 Main Feature)
- Find events near any location using latitude/longitude
- Perfect for: "Find events near my meeting location"
- Uses Haversine formula for accurate distance calculations
- Returns results sorted by distance with km/miles info

### 2. **Flexible Search & Filtering**
- Search by keyword (title, description, venue)
- Filter by category (music, museum, pop-ups, football, movies)
- Filter by date range
- Combine multiple filters for precise results

### 3. **Easy Integration**
- Works with Claude Desktop
- Designed to work alongside Google Calendar MCP
- Supports both stdio and SSE modes
- Simple configuration

## 📁 Project Structure

```
nyc_events_mcp/
├── src/
│   └── nyc_events_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py                    # Main MCP server
│       └── tools/
│           ├── __init__.py
│           ├── toolhandler.py           # Base handler class
│           ├── events_service.py        # Database operations & distance calc
│           └── tools_events.py          # 6 tool implementations
├── requirements.txt
├── pyproject.toml
├── run.sh                               # Startup script
├── README.md                            # Full documentation
├── QUICKSTART.md                        # 2-minute setup guide
├── USAGE_EXAMPLES.md                    # Integration patterns
└── claude_desktop_config.example.json   # Sample config
```

## 🛠️ Tools Implemented

| Tool Name | Purpose |
|-----------|---------|
| `search_events` | Free-text search with multiple filters |
| `get_events_by_category` | Get all events in a category |
| `get_events_by_date_range` | Find events in date range |
| `find_events_near_location` | **Proximity search** (key feature) |
| `get_event_by_id` | Get specific event details |
| `get_event_categories` | List available categories |

## 🗄️ Database Schema

Your SQLite database (`events_oct20_to_nov20_2025_nyc.sqlite`) contains:

- **155 events** across 5 categories
- **Date range**: October 20 - November 20, 2025
- **Categories**: music, museum, pop-ups, football, movies
- **Each event has**: ID, title, category, date, times, venue, lat/long, description

## 🚀 How It Works

### Basic Usage
```
User → "Find music events near Times Square"
         ↓
Claude → Uses NYC Events MCP
         ↓
Server → Queries database with proximity search
         ↓
Claude → Returns formatted results with distances
```

### Integration with Calendar
```
User → "Find events near my 2pm meeting tomorrow"
         ↓
Claude → Uses Calendar MCP to get meeting location
         ↓
Claude → Uses Events MCP with coordinates
         ↓
Claude → Filters by time and presents options
         ↓
User → "Add the museum event to my calendar"
         ↓
Claude → Uses Calendar MCP to create event
```

## 💡 Example Queries

### Query 1: Category-Based
```
User: "What museums can I visit this weekend?"

MCP Call: get_events_by_category
- category: "museum"
- start_date: "2025-10-25"
- end_date: "2025-10-26"
```

### Query 2: Proximity-Based (🌟 Key Feature)
```
User: "I have a meeting at Chelsea Market. What's nearby?"

MCP Call: find_events_near_location
- latitude: 40.7424
- longitude: -74.0061
- radius_km: 2.0
```

### Query 3: Combined Filters
```
User: "Find pop-up events near Times Square next Tuesday"

MCP Call: find_events_near_location
- latitude: 40.7580
- longitude: -73.9855
- radius_km: 2.0
- category: "pop-ups"
- start_date: "2025-10-28"
- end_date: "2025-10-28"
```

## 🔌 Integration Setup

### Claude Desktop Configuration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nyc-events": {
      "command": "python",
      "args": ["-m", "nyc_events_mcp.server"],
      "cwd": "/Users/tanishqsardana/Desktop/Codes/morning_me",
      "env": {
        "PYTHONPATH": "/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src"
      }
    }
  }
}
```

## 🏗️ Architecture

### Design Pattern
Follows the same modular architecture as your `mcp_weather_server`:
- **Extensible**: Easy to add new tools
- **Modular**: Separate concerns (server, tools, service)
- **Testable**: Each component can be tested independently

### Key Components

1. **EventsService** (`events_service.py`)
   - Handles all database operations
   - Implements Haversine distance calculation
   - Formats results for display

2. **Tool Handlers** (`tools_events.py`)
   - 6 tool implementations
   - Each extends base `ToolHandler` class
   - Async support for future API integration

3. **MCP Server** (`server.py`)
   - Registers all tools
   - Handles MCP protocol
   - Supports stdio and SSE modes

## ✅ Testing

The server was tested and verified:
- ✓ Database connection works
- ✓ All query types function correctly
- ✓ Distance calculations are accurate
- ✓ Results are properly formatted
- ✓ Integration with existing Python environment

## 🎉 Ready to Use

The NYC Events MCP server is:
- ✅ Fully implemented
- ✅ Tested and working
- ✅ Documented with guides
- ✅ Ready for Claude Desktop integration
- ✅ Compatible with Calendar MCP

## 📖 Documentation Files

1. **QUICKSTART.md** - 2-minute setup guide
2. **README.md** - Complete documentation
3. **USAGE_EXAMPLES.md** - Integration patterns and examples
4. **claude_desktop_config.example.json** - Sample configuration

## 🎯 Next Steps

1. **Add to Claude Desktop**
   - Copy configuration to Claude config file
   - Restart Claude Desktop
   
2. **Try It Out**
   - Ask Claude about NYC events
   - Test proximity search
   - Combine with Calendar MCP

3. **Customize (Optional)**
   - Add more tool handlers if needed
   - Adjust default search radius
   - Add additional filters

## 🌟 Standout Features

1. **Proximity Search**: The key feature for calendar integration
2. **Complete Integration**: Works seamlessly with your existing Calendar MCP
3. **Production Ready**: Error handling, logging, and robust code
4. **Well Documented**: Multiple guides for different use cases
5. **Extensible**: Easy to add new features following the same pattern

---

**Built for**: morning_me workspace  
**Database**: events_oct20_to_nov20_2025_nyc.sqlite (155 events)  
**Integration**: Claude Desktop + Google Calendar MCP  
**Status**: ✅ Complete and Ready to Use


