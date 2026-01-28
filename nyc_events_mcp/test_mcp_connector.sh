#!/bin/bash
# Quick test script before running MCP Connector

set -e  # Exit on error

echo "================================================================================"
echo "NYC Events MCP Server - Pre-Connector Test"
echo "================================================================================"
echo ""

# Change to workspace root
cd /Users/tanishqsardana/Desktop/Codes/morning_me

# Test 1: Check Python
echo "✓ Checking Python..."
python --version
echo ""

# Test 2: Check database
echo "✓ Checking database..."
if [ -f "events_oct20_to_nov20_2025_nyc.sqlite" ]; then
    echo "  Database found: events_oct20_to_nov20_2025_nyc.sqlite"
    EVENT_COUNT=$(sqlite3 events_oct20_to_nov20_2025_nyc.sqlite "SELECT COUNT(*) FROM events;")
    echo "  Total events: ${EVENT_COUNT}"
else
    echo "  ❌ ERROR: Database not found!"
    exit 1
fi
echo ""

# Test 3: Check Python packages
echo "✓ Checking Python packages..."
python -c "import mcp; print('  - mcp: OK')"
python -c "import sqlite3; print('  - sqlite3: OK')"
echo ""

# Test 4: Test EventsService
echo "✓ Testing EventsService initialization..."
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"
python -c "import sys; sys.path.insert(0, 'nyc_events_mcp/src'); from nyc_events_mcp.tools.events_service import EventsService; es = EventsService(); print('  EventsService initialized successfully')"
echo ""

# Test 5: Check npx (for MCP Connector)
echo "✓ Checking npx availability..."
if command -v npx &> /dev/null; then
    npx --version
    echo "  npx is available"
else
    echo "  ⚠️  WARNING: npx not found. You'll need Node.js installed."
    echo "  Install from: https://nodejs.org/"
fi
echo ""

echo "================================================================================"
echo "Pre-flight checks complete!"
echo "================================================================================"
echo ""
echo "To test with MCP Connector, run:"
echo ""
echo "  cd /Users/tanishqsardana/Desktop/Codes/morning_me"
echo "  export PYTHONPATH=\"/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:\${PYTHONPATH}\""
echo "  npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server"
echo ""
echo "This will open a browser with the MCP Connector interface."
echo "You can then test all 6 tools interactively!"
echo ""



