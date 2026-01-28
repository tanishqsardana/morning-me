#!/bin/bash
# Launch NYC Events MCP Server with MCP Connector

set -e

echo "🚀 Starting NYC Events MCP Server with MCP Connector..."
echo ""

# Navigate to workspace root
cd /Users/tanishqsardana/Desktop/Codes/morning_me

# Set PYTHONPATH
export PYTHONPATH="/Users/tanishqsardana/Desktop/Codes/morning_me/nyc_events_mcp/src:${PYTHONPATH}"

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✓ Environment configured"
echo "✓ Starting MCP Connector..."
echo ""
echo "📝 MCP Connector will:"
echo "   1. Start the NYC Events server"
echo "   2. Open your browser at http://localhost:5173"
echo "   3. Show all 6 available tools"
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""

# Launch MCP Connector
npx @modelcontextprotocol/inspector python -m nyc_events_mcp.server



