# NYC Events MCP Server - Quick Start Guide

## 🚀 Setup (2 minutes)

### 1. Verify Requirements
```bash
# Check Python version (requires 3.10+)
python --version

# Verify you have the required packages
python -c "import mcp, sqlite3; print('✓ All dependencies available')"
```

### 2. Test the Server
```bash
# Run from the workspace root
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp

# Quick test (should initialize without errors)
python -c "import sys; sys.path.insert(0, 'src'); from nyc_events_mcp.tools.events_service import EventsService; es = EventsService(); print('✓ Server ready!')"
```

### 3. Configure Claude Desktop

**For macOS**, edit:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Add this configuration:**
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

### 4. Restart Claude Desktop

After saving the config, restart Claude Desktop app. The NYC Events server will be available.

## ✅ Verify It's Working

### Option A: Test with MCP Connector (Recommended for Testing)

MCP Connector lets you test the server in a web interface before integrating with Claude:

```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
```

This will:
- Open a browser at http://localhost:5173
- Show all 6 available tools
- Let you test each tool interactively

**See `TEST_WITH_MCP_CONNECTOR.md` for detailed instructions and test cases.**

### Option B: Test with Claude Desktop

In Claude, try asking:
> "What events are available in NYC next week?"

Or:
> "Find music events near Times Square"

You should see the server responding with event information.

## 🎯 Quick Examples

### Example 1: Find Events by Category
```
You: "Show me museum events this week"
```

### Example 2: Location-Based Search
```
You: "I'll be near Central Park tomorrow. What events are nearby?"
```

### Example 3: Date-Based Search
```
You: "What's happening on Halloween?"
```

### Example 4: Combined with Calendar
```
You: "I have a meeting at Chelsea Market tomorrow at 2pm. 
     Find events I can attend nearby after 4pm."
```

## 📊 Database Info

- **Coverage**: October 20 - November 20, 2025
- **Categories**: music, museum, pop-ups, football, movies
- **Total Events**: 155 events
- **Location**: All events in New York City with coordinates

## 🔧 Available Tools

1. **search_events** - Free-text search with filters
2. **get_events_by_category** - Filter by event type
3. **get_events_by_date_range** - Find events in date range
4. **find_events_near_location** - Proximity search (🌟 key feature)
5. **get_event_by_id** - Get specific event details
6. **get_event_categories** - List all categories

## 🗺️ Common NYC Coordinates

For proximity searches:
- Times Square: `40.7580, -73.9855`
- MoMA: `40.7614, -73.9776`
- Chelsea Market: `40.7424, -74.0061`
- Central Park: `40.7829, -73.9654`

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Verify database exists
ls -la /Users/tanishqsardana/Desktop/Codes/morning_me/events_oct20_to_nov20_2025_nyc.sqlite
```

### No events found?
- Ensure dates are within Oct 20 - Nov 20, 2025
- Try increasing `radius_km` for location searches
- Remove filters to see all events

### Database error?
- Verify the database file is in workspace root
- Check file permissions: `chmod 644 events_oct20_to_nov20_2025_nyc.sqlite`

## 📚 More Information

- See `README.md` for detailed documentation
- See `USAGE_EXAMPLES.md` for integration patterns with Calendar agent
- See `claude_desktop_config.example.json` for multi-server setup

## 🎉 You're Ready!

The NYC Events MCP server is now integrated with Claude and ready to help you discover events in New York City. Try combining it with your Google Calendar MCP server for powerful event discovery and scheduling!

