# NYC Events MCP Server - Setup Checklist

## ✅ Pre-flight Checklist

### 1. Verify Database
- [ ] Database file exists: `events_oct20_to_nov20_2025_nyc.sqlite`
- [ ] Located at: `/Users/tanishqsardana/Desktop/Codes/morning_me/`
- [ ] Contains 155 events

```bash
# Verify database
cd /Users/tanishqsardana/Desktop/Codes/morning_me
ls -lh events_oct20_to_nov20_2025_nyc.sqlite
sqlite3 events_oct20_to_nov20_2025_nyc.sqlite "SELECT COUNT(*) FROM events;"
```

### 2. Verify Python Environment
- [ ] Python 3.10+ installed
- [ ] Required packages available (mcp, sqlite3)

```bash
# Check Python version
python --version

# Check packages
python -c "import mcp, sqlite3; print('✓ All packages available')"
```

### 3. Test the Server
- [ ] Server can initialize
- [ ] Database connection works
- [ ] Queries return results

```bash
# Run demo
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
python demo.py
```

### 4. Claude Desktop Integration
- [ ] Config file location identified
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

- [ ] Configuration added:
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

- [ ] Claude Desktop restarted
- [ ] Server appears in Claude's available tools

### 5. Test in Claude
- [ ] Ask: "What categories of events are available?"
- [ ] Ask: "Find music events near Times Square"
- [ ] Ask: "What's happening on October 25th?"

## 🚀 Quick Commands

### Test Database Connection
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
python -c "import sys; sys.path.insert(0, 'src'); from nyc_events_mcp.tools.events_service import EventsService; es = EventsService(); print('✓ Server ready!')"
```

### Run Demo
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp
python demo.py
```

### Start Server Manually (stdio mode)
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me
python -m nyc_events_mcp.server
```

### Start Server Manually (SSE mode)
```bash
cd /Users/tanishqsardana/Desktop/Codes/morning_me
python -m nyc_events_mcp.server --mode sse --port 8080
```

## 🎯 What Success Looks Like

### In Terminal (demo.py)
You should see:
- ✓ Database statistics (155 events, 5 categories)
- ✓ Proximity search results with distances
- ✓ Event details formatted nicely
- ✓ No error messages

### In Claude Desktop
You should see:
- ✓ Server listed in available tools
- ✓ Can ask about NYC events
- ✓ Results include event details and locations
- ✓ Proximity search works with coordinates

## 🐛 Troubleshooting

### Issue: "Database not found"
**Solution:**
```bash
# Verify database location
ls -la /Users/tanishqsardana/Desktop/Codes/morning_me/*.sqlite

# If database is elsewhere, update EventsService.__init__ or pass db_path
```

### Issue: "Module not found"
**Solution:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:$PYTHONPATH"

# Or update Claude config with PYTHONPATH in env section
```

### Issue: "Server not showing in Claude"
**Solution:**
1. Check Claude config JSON syntax (use JSONLint)
2. Verify paths are absolute (not ~)
3. Restart Claude Desktop completely
4. Check Claude logs for errors

### Issue: "No events found"
**Solution:**
- Ensure date is between Oct 20 - Nov 20, 2025
- Increase radius_km for location searches
- Remove filters to see all events
- Check database has data: `sqlite3 events_oct20_to_nov20_2025_nyc.sqlite "SELECT COUNT(*) FROM events;"`

## 📚 Documentation Reference

- **QUICKSTART.md** - Fast setup guide
- **README.md** - Complete documentation
- **USAGE_EXAMPLES.md** - Integration patterns
- **demo.py** - Live demonstration

## ✨ Optional: Multi-Server Setup

To use NYC Events alongside Google Calendar MCP:

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
    },
    "google-calendar": {
      "command": "node",
      "args": [
        "/Users/tanishqsardana/Desktop/Codes/morning_me/google-calendar-mcp/build/index.js"
      ]
    }
  }
}
```

## 🎉 Ready!

Once all checkboxes are ✓, you're ready to use the NYC Events MCP server!

Try asking Claude:
- "Find events near my next meeting"
- "What museums are open this weekend?"
- "Show me pop-up events in Manhattan"



