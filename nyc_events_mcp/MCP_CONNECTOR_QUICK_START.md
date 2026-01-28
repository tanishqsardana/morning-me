# MCP Connector - Quick Start (30 seconds)

## 🚀 One Command to Test Everything

```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me && \
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}" && \
npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server
```

**What happens:**
1. Terminal shows server starting
2. Browser opens at http://localhost:5173
3. You see "nyc-events-mcp-server" connected
4. Click on it to see all 6 tools

## 🧪 Quick Test Cases

Once MCP Connector opens, try these:

### Test 1: Get Categories
- Tool: `get_event_categories`
- Args: `{}`
- Expected: 5 categories listed

### Test 2: Find Near Times Square
- Tool: `find_events_near_location`
- Args:
  ```json
  {
    "latitude": 40.7580,
    "longitude": -73.9855,
    "radius_km": 2.0
  }
  ```
- Expected: Events with distances shown

### Test 3: Search Museums
- Tool: `get_events_by_category`
- Args:
  ```json
  {
    "category": "museum",
    "limit": 3
  }
  ```
- Expected: 3 museum events

## 💡 Tips

- **Left sidebar**: Select your server
- **Middle panel**: Click on any tool
- **Right panel**: Fill in parameters and click "Run"
- **Bottom panel**: See the response

## ❌ If Something Goes Wrong

**"Module not found"**
```bash
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
```

**"Database not found"**
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me
ls events_oct20_to_nov20_2025_nyc.sqlite  # Should exist
```

**"npx not found"**
Install Node.js from https://nodejs.org/

## ✅ Success Looks Like

- ✓ Browser opens automatically
- ✓ Server shows as "Connected"
- ✓ 6 tools are listed
- ✓ Clicking a tool shows its parameters
- ✓ Running a tool returns formatted results

## 📖 More Details

See `TEST_WITH_MCP_CONNECTOR.md` for:
- All 6 test cases with expected results
- Troubleshooting guide
- Alternative testing methods



