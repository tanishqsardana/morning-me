# Testing with MCP Connector - Complete Guide

## ✅ Yes, it works with MCP Connector!

Your NYC Events MCP server is fully compatible with MCP Connector (formerly MCP Inspector). This is the **best way to test** before integrating with Claude Desktop.

## 🚀 Quick Start (Choose One)

### Option 1: Use the Script (Easiest)
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
./test_with_mcp_connector.sh
```

### Option 2: Run Command Directly
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
```

## 🎯 What You'll See

### In Terminal
```
Starting MCP Connector...
Server: nyc-events-mcp-server connected
Tools available: 6
Local: http://localhost:5173/
```

### In Browser
1. **Left Sidebar**: Your server listed as "nyc-events-mcp-server" ✅
2. **Main Panel**: Click the server to see 6 tools
3. **Tool Details**: Click any tool to see its parameters
4. **Test Interface**: Fill in parameters and click "Run"
5. **Results Panel**: See formatted responses

## 📋 6 Tools to Test

| # | Tool Name | Test This |
|---|-----------|-----------|
| 1 | `get_event_categories` | No params needed - just click Run |
| 2 | `search_events` | Try: `{"query": "Gallery"}` |
| 3 | `get_events_by_category` | Try: `{"category": "museum"}` |
| 4 | `get_events_by_date_range` | Try: `{"start_date": "2025-10-25", "end_date": "2025-10-27"}` |
| 5 | `find_events_near_location` | Try: `{"latitude": 40.7580, "longitude": -73.9855, "radius_km": 2.0}` ⭐ |
| 6 | `get_event_by_id` | Copy an event_id from another query result |

## 🌟 Must-Try Test Case (Proximity Search)

This is the **key feature** for calendar integration:

**Tool**: `find_events_near_location`

**Parameters**:
```json
{
  "latitude": 40.7580,
  "longitude": -73.9855,
  "radius_km": 2.0,
  "category": "museum",
  "limit": 5
}
```

**What to expect**:
- Events sorted by distance from Times Square
- Distance shown in both km and miles
- All within 2km radius
- Only museum category events

## 🎨 Visual Guide

```
┌─────────────────────────────────────────────────────────┐
│ MCP Connector                                    ×      │
├──────────┬──────────────────────────────────────────────┤
│ Servers  │ Tools                                        │
│          │                                              │
│ ✅ nyc-  │ 📍 find_events_near_location                │
│  events- │ 🔍 search_events                            │
│  mcp     │ 📅 get_events_by_date_range                 │
│          │ 🎭 get_events_by_category                   │
│          │ 🆔 get_event_by_id                          │
│          │ 📋 get_event_categories                     │
│          │                                              │
│          ├──────────────────────────────────────────────┤
│          │ Test Interface:                             │
│          │ latitude: [40.7580]                         │
│          │ longitude: [-73.9855]                       │
│          │ radius_km: [2.0]                            │
│          │ [Run Tool]                                  │
│          │                                              │
│          ├──────────────────────────────────────────────┤
│          │ Results:                                     │
│          │ Found 3 events within 2km:                  │
│          │ 1. Feature Screening @ AMC Empire 25        │
│          │    Distance: 0.37 km (0.23 miles)          │
│          │    ...                                       │
└──────────┴──────────────────────────────────────────────┘
```

## ✨ Benefits of MCP Connector

1. **Visual Testing** - See all tools at once
2. **Interactive** - Test with different parameters
3. **Instant Feedback** - See results immediately
4. **No Restart** - Test changes quickly
5. **Debug Friendly** - See error messages clearly

## 🔄 Workflow

1. **Run MCP Connector** → Opens browser
2. **Select Server** → Click "nyc-events-mcp-server"
3. **Choose Tool** → Click any of the 6 tools
4. **Fill Parameters** → Enter test values
5. **Run** → See results
6. **Iterate** → Try different parameters
7. **Verify** → All tools working? ✅
8. **Deploy** → Add to Claude Desktop config

## 🛠️ Pre-flight Check

Run this before testing:
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
./test_mcp_connector.sh
```

This verifies:
- ✓ Python is available
- ✓ Database exists (155 events)
- ✓ Packages are installed
- ✓ Server can initialize
- ✓ npx is available

## 📝 Test Scenarios

### Scenario 1: Basic Functionality
```
1. get_event_categories → Should return 5 categories
2. get_events_by_category(museum) → Should return museum events
3. search_events(Gallery) → Should return events with "Gallery"
```

### Scenario 2: Date Filtering
```
1. get_events_by_date_range(2025-10-25, 2025-10-27)
2. Verify results are within date range
3. Try different dates
```

### Scenario 3: Proximity Search (Key Feature! ⭐)
```
1. find_events_near_location(Times Square coords)
2. Verify distances are calculated
3. Verify results are sorted by distance
4. Try different radius values
5. Add category filter
6. Add date filter
```

### Scenario 4: Integration Simulation
```
Simulate calendar integration:
1. Pick a venue (e.g., Chelsea Market: 40.7424, -74.0061)
2. Use find_events_near_location with those coords
3. Add date filter for "tomorrow"
4. Add category filter for interest
5. See what you'd recommend to user
```

## 🎓 Learning the Tools

### Tool 1: `get_event_categories`
**Purpose**: Discover what categories exist
**Params**: None
**Use**: "What types of events are available?"

### Tool 2: `search_events`
**Purpose**: Free-text search
**Params**: query, category?, date filters?, limit?
**Use**: "Find events matching a keyword"

### Tool 3: `get_events_by_category`
**Purpose**: Browse by event type
**Params**: category (required), date filters?, limit?
**Use**: "Show me all museums"

### Tool 4: `get_events_by_date_range`
**Purpose**: Events in time period
**Params**: start_date, end_date (required), category?, limit?
**Use**: "What's happening this weekend?"

### Tool 5: `find_events_near_location` ⭐
**Purpose**: Proximity search (KEY FEATURE!)
**Params**: lat, lon (required), radius?, category?, dates?, limit?
**Use**: "Find events near my meeting location"

### Tool 6: `get_event_by_id`
**Purpose**: Get specific event details
**Params**: event_id (required)
**Use**: "Tell me more about this event"

## 🚨 Common Issues

### Browser doesn't open
- Manually go to http://localhost:5173
- Check terminal for the correct URL

### "Connection failed"
- Check PYTHONPATH is set correctly
- Verify you're in the right directory
- Run `./test_mcp_connector.sh` to check setup

### "No tools showing"
- Wait a few seconds for server to connect
- Check terminal for error messages
- Verify database exists

### "Module not found"
- Export PYTHONPATH before running:
  ```bash
  export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
  ```

## ✅ Success Checklist

- [ ] MCP Connector opens in browser
- [ ] Server shows as "Connected"
- [ ] All 6 tools are visible
- [ ] `get_event_categories` returns 5 categories
- [ ] `get_events_by_category` returns results
- [ ] `search_events` finds matching events
- [ ] `get_events_by_date_range` filters by date
- [ ] `find_events_near_location` calculates distances ⭐
- [ ] Results are properly formatted
- [ ] No error messages in terminal

## 📚 Next Steps

After successful testing:

1. ✅ **Verified** - All tools work in MCP Connector
2. ➡️ **Deploy** - Add to Claude Desktop config
3. 🎯 **Integrate** - Combine with Google Calendar MCP
4. 🎉 **Use** - Ask Claude about NYC events!

## 🎬 Ready to Test?

Run this now:
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
./test_with_mcp_connector.sh
```

Your browser will open, and you can start testing immediately!

---

**Pro Tip**: Keep MCP Connector open while developing. You can test changes quickly without restarting Claude Desktop.



