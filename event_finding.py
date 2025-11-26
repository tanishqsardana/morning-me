"""
MCP Server (mcp 1.16.x) — NYC Events SQLite

Run (SSE):
python event_finding.py --mode sse --host 0.0.0.0 --port 3002 --db events_oct20_to_nov20_2025_nyc.sqlite
"""
from __future__ import annotations
import argparse, json, math, os, sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP  # <-- correct for 1.16.x
from mcp.server.sse import run as run_sse  # SSE runner

EARTH_R_KM = 6371.0
def haversine_km(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, asin, sqrt
    dlat = radians(lat2 - lat1); dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * asin(min(1.0, math.sqrt(a)))
    return EARTH_R_KM * c

class EventDB:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"SQLite DB not found: {path}")
        self.path = path
    def conn(self): return sqlite3.connect(self.path)

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self.conn() as con:
            cur = con.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
            row = cur.fetchone()
            if not row: return None
            cols = [c[0] for c in cur.description]
            return dict(zip(cols, row))

    def search(self, date_start: str, date_end: str,
               category: Optional[str]=None,
               near_lat: Optional[float]=None, near_lon: Optional[float]=None,
               within_km: Optional[float]=None, limit: int=20) -> List[Dict[str, Any]]:
        q = ["SELECT * FROM events WHERE date >= ? AND date <= ?"]
        args: List[Any] = [date_start, date_end]
        if category:
            q.append("AND category = ?"); args.append(category)
        q.append("ORDER BY date, start_time_local")
        sql = " ".join(q)
        with self.conn() as con:
            cur = con.execute(sql, tuple(args))
            cols = [c[0] for c in cur.description]
            out = [dict(zip(cols, row)) for row in cur.fetchall()]
        if near_lat is not None and near_lon is not None and within_km is not None:
            out = [r for r in out if haversine_km(float(near_lat), float(near_lon),
                                                  float(r["latitude"]), float(r["longitude"])) <= float(within_km)]
            out.sort(key=lambda r: haversine_km(float(near_lat), float(near_lon),
                                                float(r["latitude"]), float(r["longitude"])))
        return out[: max(1, int(limit))]

def build_server(db: EventDB) -> FastMCP:
    mcp = FastMCP("nyc-events")

    @mcp.tool()
    def search_events(
        date_start: str,
        date_end: str,
        category: Optional[str] = None,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        within_km: Optional[float] = None,
        limit: int = 20,
    ) -> str:
        """Search events (YYYY-MM-DD range). Optional: category and/or proximity (near_lat/near_lon/within_km)."""
        _ = datetime.fromisoformat(date_start); _ = datetime.fromisoformat(date_end)
        res = db.search(date_start, date_end, category, near_lat, near_lon, within_km, limit)
        return json.dumps(res)

    @mcp.tool()
    def get_event_by_id(event_id: str) -> str:
        """Return one event by ID."""
        evt = db.get_event(event_id)
        return json.dumps(evt if evt else {"error": f"event_id not found: {event_id}"})

    @mcp.tool()
    def rank_by_near_event(
        event_id: str,
        category: Optional[str] = None,
        date: Optional[str] = None,
        within_km: Optional[float] = 2.0,
        limit: int = 20,
    ) -> str:
        """Rank events near the given event (same date by default)."""
        src = db.get_event(event_id)
        if not src:
            return json.dumps({"error": f"event_id not found: {event_id}"})
        lat0, lon0 = float(src["latitude"]), float(src["longitude"])
        dstart = dend = date if date else src["date"]
        res = db.search(dstart, dend, category, lat0, lon0, within_km, limit)
        res = [r for r in res if r["event_id"] != event_id]
        return json.dumps(res)

    return mcp

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--mode", default="sse", choices=["sse"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3002)
    args = ap.parse_args()

    db = EventDB(args.db)
    server = build_server(db)
    if args.mode == "sse":
        run_sse(server, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
