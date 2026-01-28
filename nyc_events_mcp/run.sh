#!/bin/bash
# Startup script for NYC Events MCP Server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Default to stdio mode
MODE="${1:-stdio}"

echo "Starting NYC Events MCP Server in ${MODE} mode..."
echo "Database: ${SCRIPT_DIR}/../events_oct20_to_nov20_2025_nyc.sqlite"
echo ""

cd "${SCRIPT_DIR}/.."
python -m nyc_events_mcp.server --mode "${MODE}"


