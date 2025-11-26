in morningme folder - open-webui serve
in google_calendar_mcp - mcpo --port 8000 -- npm start
in morningme folder - python -m nyc_events_mcp.server --mode sse --host 0.0.0.0 --port 8022

in morningme/nyc_events_mcp - uvx mcpo --port 8023 --server-type sse -- http://127.0.0.1:8022/sse
