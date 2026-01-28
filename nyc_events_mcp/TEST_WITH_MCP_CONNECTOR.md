# Testing NYC Events MCP with MCP Connector

## What is MCP Connector?

MCP Connector (formerly MCP Inspector) is a web-based tool for testing and debugging MCP servers. It's perfect for verifying your server works before integrating with Claude Desktop.

## Setup & Testing

### Method 1: Direct Connection (Recommended)

1. **Start the MCP Connector**:
   ```bash
   npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
   ```

2. **If that doesn't work, set the full path**:
   ```bash
   cd /Users/tanishqsardana/Desktop/Codes/morning_me
   npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
   ```

3. **Or use the startup script**:
   ```bash
   cd /Users/tanishqsardana/Desktop/Codes/morning_me
   export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
   npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
   ```

4. **MCP Connector will**:
   - Start a web server (usually on http://localhost:5173)
   - Open your browser automatically
   - Connect to your NYC Events server

### Method 2: Using Config File

If you prefer using a config file, create `mcp_config.json`:

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

Then run:
```bash
npx @modelcontextprotocol/inspector mcp_config.json
```

## What You'll See in MCP Connector

### 1. Server Information
- Server name: `nyc-events-mcp-server`
- Status: Connected ✅

### 2. Available Tools (6 total)
You should see all 6 tools listed:
- ✅ `search_events`
- ✅ `get_events_by_category`
- ✅ `get_events_by_date_range`
- ✅ `find_events_near_location`
- ✅ `get_event_by_id`
- ✅ `get_event_categories`

### 3. Interactive Testing
You can click on each tool and test it with parameters.

## Test Cases to Try

### Test 1: List Categories
**Tool**: `get_event_categories`
**Arguments**: `{}` (empty)
**Expected Result**: List of 5 categories (football, movies, museum, music, pop-ups)

### Test 2: Search Near Times Square
**Tool**: `find_events_near_location`
**Arguments**:
```json
{
  "latitude": 40.7580,
  "longitude": -73.9855,
  "radius_km": 2.0,
  "limit": 5
}
```
**Expected Result**: Events within 2km with distance information

### Test 3: Get Museum Events
**Tool**: `get_events_by_category`
**Arguments**:
```json
{
  "category": "museum",
  "limit": 5
}
```
**Expected Result**: List of museum events

### Test 4: Search by Keyword
**Tool**: `search_events`
**Arguments**:
```json
{
  "query": "Gallery",
  "limit": 3
}
```
**Expected Result**: Events with "Gallery" in title/description/venue

### Test 5: Date Range Query
**Tool**: `get_events_by_date_range`
**Arguments**:
```json
{
  "start_date": "2025-10-25",
  "end_date": "2025-10-27",
  "limit": 10
}
```
**Expected Result**: Events between Oct 25-27, 2025

### Test 6: Combined Filters
**Tool**: `find_events_near_location`
**Arguments**:
```json
{
  "latitude": 40.7424,
  "longitude": -74.0061,
  "radius_km": 1.5,
  "category": "pop-ups",
  "start_date": "2025-10-20",
  "end_date": "2025-10-31"
}
```
**Expected Result**: Pop-up events near Chelsea Market in late October

## Troubleshooting

### Issue: "Command not found: npx"
**Solution**: Install Node.js from https://nodejs.org/

### Issue: "Module not found: nyc_events_mcp"
**Solution**: Make sure PYTHONPATH is set correctly:
```bash
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
```

### Issue: "Database not found"
**Solution**: Verify you're running from the correct directory:
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me
ls -la events_oct20_to_nov20_2025_nyc.sqlite
```

### Issue: Port already in use
**Solution**: MCP Connector uses port 5173 by default. If it's busy:
```bash
# Kill the process using the port
lsof -ti:5173 | xargs kill -9

# Or just restart your terminal
```

### Issue: Browser doesn't open automatically
**Solution**: Manually open http://localhost:5173 in your browser

## Expected Output in Terminal

When you start MCP Connector, you should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help

Server: nyc-events-mcp-server connected
Tools available: 6
```

## Benefits of Testing with MCP Connector

1. **See all tools** - Visual list of all available tools
2. **Test parameters** - Interactive forms for testing each tool
3. **See responses** - View formatted results immediately
4. **Debug issues** - Check for errors before Claude Desktop integration
5. **No restart needed** - Unlike Claude Desktop, you can modify and test quickly

## After Testing Successfully

Once everything works in MCP Connector:
1. ✅ Your server is working correctly
2. ✅ All tools are accessible
3. ✅ Database queries return results
4. ✅ Ready to integrate with Claude Desktop

## Alternative: Test with Python Directly

If you don't want to use MCP Connector, run the demo script:
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
python demo.py
```

This will show you all capabilities without needing Node.js or MCP Connector.

## Video/Screenshot Reference

When MCP Connector opens, you'll see:
- Left sidebar: List of connected servers
- Main panel: Available tools for selected server
- Right panel: Tool details and test interface
- Bottom panel: Request/response logs

Click on "nyc-events" in the left sidebar to see all 6 tools, then click on any tool to test it!



