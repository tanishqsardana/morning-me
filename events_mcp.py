"""
MCP Events Discovery Server (Tavily-powered)
============================================

A minimal MCP server that discovers local events using the Tavily web search API
and returns structured results. Includes convenience tools for common queries
like "this weekend". Built with FastMCP.

Quick start
-----------
1) Install deps:
   pip install fastmcp httpx python-dateutil pydantic selectolax

2) Set your API key:
   export TAVILY_API_KEY=sk_tavily_...

3) Run (stdio mode by default):
   python server.py --mode stdio

   Or SSE mode:
   python server.py --mode sse --host 0.0.0.0 --port 3002

4) Add to your client (Open WebUI / Claude Desktop / etc.) as an MCP server.

Provided tools
--------------
- search_events(query, location, start_date, end_date, max_results)
    General-purpose search with ISO8601 dates. Returns normalized list of events.

- weekend_guide(location, interests, weekend_offset)
    Convenience wrapper for the upcoming (or offset) weekend.

- summarize_url(url)
    Pulls a single page via Tavily and extracts any event-like info.

- luma_discover(query, location, start_date?, end_date?, max_results?, calendar_ready?, ...)
    Uses Tavily **only to discover Lu.ma URLs**, then fetches and parses each page’s JSON-LD for exact start/end/venue.

- luma_scrape_url(url, calendar_ready?, ...)
    Fetches a single Lu.ma event/collection URL and extracts JSON-LD Events directly (no search).

Notes
-----
- Tavily API docs: https://docs.tavily.com (search endpoint)
- This server *does not* scrape aggressively; it uses Tavily's summary payloads
  and titles/snippets. For richer data, you can attach a headless browser fetcher
  and HTML parser.
"""

from __future__ import annotations

import os
import json
import re
import argparse
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse
import uuid

import httpx
from dateutil import tz
from dateutil.parser import isoparse
from pydantic import BaseModel, Field
from fastmcp import FastMCP, Context
from selectolax.parser import HTMLParser

# -----------------------------
# Config
# -----------------------------
TAVILY_API_URL = "https://api.tavily.com/search"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
DEFAULT_TIMEZONE = os.getenv("EVENTS_TZ", "America/New_York")
TAVILY_TIMEOUT = float(os.getenv("TAVILY_TIMEOUT", "12"))  # seconds

# Default allow/deny lists to bias toward real event listings
DEFAULT_INCLUDE_DOMAINS = [
    "eventbrite.com", "lu.ma", "meetup.com", "dice.fm", "songkick.com",
    "ra.co", "bandsintown.com", "ticketmaster.com", "jazz.org",
    "bluenotejazz.com", "birdlandjazz.com", "hothousejazz.com",
    "timeout.com", "nycgovparks.org", "lincolncenter.org"
]
DEFAULT_EXCLUDE_DOMAINS = [
    "youtube.com", "youtu.be", "reddit.com", "x.com", "twitter.com",
    "tiktok.com", "facebook.com", "instagram.com"
]

# Common event keywords to bias Tavily toward listings
EVENT_KEYWORDS = [
    "events", "concerts", "festival", "meetup", "conference", "workshop",
    "exhibition", "show", "comedy", "theatre", "sports", "talk", "seminar",
]

# -----------------------------
# Schemas
# -----------------------------
class Event(BaseModel):
    title: str
    url: str
    start_datetime: Optional[str] = Field(None, description="ISO8601 if available")
    end_datetime: Optional[str] = None
    venue: Optional[str] = None
    location: Optional[str] = None
    price: Optional[str] = None
    source: Optional[str] = None
    snippet: Optional[str] = None
    # calendar-friendly enrichments (optional)
    gcal_url: Optional[str] = None
    ics: Optional[str] = None

class SearchEventsArgs(BaseModel):
    query: str = Field(..., description="Free-text event query; we'll augment with keywords.")
    location: str = Field(..., description="City or area, e.g. 'New York, NY'.")
    start_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="YYYY-MM-DD (inclusive)")
    max_results: int = Field(8, ge=1, le=50)
    # calendarization options
    calendarize: bool = Field(False, description="Add Google Calendar link and ICS text per event (when start time is known)")
    duration_minutes: int = Field(120, ge=15, le=24*60, description="Default duration if end time is unknown")
    calendar_ready: bool = Field(False, description="Return minimal, clean calendar payloads {title,start,end,timezone,location,description,url}")
    default_start_time: str = Field("19:00", description="HH:MM (24h) used when only a date is present and no time is parsed")
    drop_unparsed: bool = Field(True, description="If true with calendar_ready, drop items without a parsable date")
    # domain controls
    include_domains: Optional[List[str]] = Field(None, description="Whitelist domains (e.g., ['eventbrite.com','lu.ma'])")
    exclude_domains: Optional[List[str]] = Field(None, description="Blacklist domains (e.g., ['youtube.com'])")
    use_default_domain_bias: bool = Field(True, description="If true, apply sensible default include/exclude domain lists")
    hard_domain_filter: bool = Field(True, description="If true, post-filter results by domain on the server side as a safety net")
    require_keywords: Optional[List[str]] = Field(default=None, description="If set, only keep items whose title/snippet contain any of these words (case-insensitive)")

class WeekendGuideArgs(BaseModel):
    location: str
    interests: Optional[List[str]] = Field(default=None, description="e.g. ['jazz','tech']")
    weekend_offset: int = Field(default=0, description="0=this weekend, 1=next weekend, etc.")
    max_results: int = Field(20, ge=1, le=50)
    calendarize: bool = Field(False, description="Add Google Calendar link and ICS text per event (when start time is known)")
    duration_minutes: int = Field(120, ge=15, le=24*60)
    calendar_ready: bool = Field(False, description="Return minimal, clean calendar payloads")
    default_start_time: str = Field("19:00")
    drop_unparsed: bool = Field(True)
    include_domains: Optional[List[str]] = Field(None)
    exclude_domains: Optional[List[str]] = Field(None)
    use_default_domain_bias: bool = Field(True)
    hard_domain_filter: bool = Field(True)
    require_keywords: Optional[List[str]] = Field(default=None)

class SummarizeUrlArgs(BaseModel):
    url: str

class LumaDiscoverArgs(BaseModel):
    query: str
    location: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_results: int = Field(10, ge=1, le=30)
    # calendar options (same defaults)
    calendar_ready: bool = False
    duration_minutes: int = Field(120, ge=15, le=24*60)
    default_start_time: str = "19:00"
    drop_unparsed: bool = True

class LumaScrapeUrlArgs(BaseModel):
    url: str
    # calendar options
    calendar_ready: bool = False
    duration_minutes: int = Field(120, ge=15, le=24*60)
    default_start_time: str = "19:00"
    drop_unparsed: bool = True

# -----------------------------
# Helpers
# -----------------------------

from datetime import datetime, timedelta
from dateutil import tz, parser as dateparser

def _dt_to_gcal_range(start: str | datetime,
                      duration_minutes: int = 120,
                      tz_name: str = "America/New_York") -> str:
    """
    Convert a start datetime (ISO string or datetime) to a Google Calendar
    time range string: 'YYYYMMDDTHHmmssZ/YYYYMMDDTHHmmssZ'.

    - If start has no time, assumes midnight in given tz.
    - Defaults to 2h duration if no end provided.
    """
    try:
        # parse ISO8601 or string
        if isinstance(start, str):
            dt = dateparser.isoparse(start)
        else:
            dt = start

        # ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz.gettz(tz_name))

        end = dt + timedelta(minutes=duration_minutes)
        # Google expects UTC times with 'Z'
        start_utc = dt.astimezone(tz.UTC)
        end_utc = end.astimezone(tz.UTC)

        fmt = "%Y%m%dT%H%M%SZ"
        return f"{start_utc.strftime(fmt)}/{end_utc.strftime(fmt)}"

    except Exception:
        return ""

# def _dt_to_gcal_range(start_iso: str, minutes: int) -> str:
#     """Return Google Calendar dates=START/END in UTC Zulu format."""
#     try:
#         start = isoparse(start_iso)
#         end = start + timedelta(minutes=minutes)
#         s = start.astimezone(tz.UTC).strftime('%Y%m%dT%H%M%SZ')
#         e = end.astimezone(tz.UTC).strftime('%Y%m%dT%H%M%SZ')
#         filtered = [e for e in events if in_window(e)]
#     # Optionally add calendar links/content
#     if args.calendarize:
#         for ev in filtered:
#             ev.gcal_url = build_gcal_url(ev.title, ev.start_datetime, args.duration_minutes, ev.venue or ev.location, ev.snippet)
#             ev.ics = build_ics(ev, args.duration_minutes)
#     filtered = [e for e in events if in_window(e)]
#     # Calendar enrichments
#     if args.calendarize:
#         for ev in filtered:
#             ev.gcal_url = build_gcal_url(ev.title, ev.start_datetime, args.duration_minutes, ev.venue or ev.location, ev.snippet)
#             ev.ics = build_ics(ev, args.duration_minutes)
#     if args.calendar_ready:
#         return _materialize_calendar(filtered, args.duration_minutes, args.default_start_time, args.drop_unparsed)
#     return filterediltered"{s}/{e}"
#     except Exception:
#         return ""


def build_gcal_url(title: str, start_iso: Optional[str], duration_minutes: int, location: Optional[str], details: Optional[str]) -> Optional[str]:
    if not start_iso:
        return None
    dates = _dt_to_gcal_range(start_iso, duration_minutes)
    if not dates:
        return None
    base = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    params = [
        ("text", title or "Event"),
        ("dates", dates),
        ("location", location or ""),
        ("details", details or "")
    ]
    qs = "&".join(f"{k}={quote(v)}" for k, v in params)
    return f"{base}&{qs}"


def build_ics(event: Event, duration_minutes: int) -> Optional[str]:
    if not event.start_datetime:
        return None
    try:
        start = isoparse(event.start_datetime)
        end = start + timedelta(minutes=duration_minutes)
        dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        dtstart = start.astimezone(tz.UTC).strftime('%Y%m%dT%H%M%SZ')
        dtend = end.astimezone(tz.UTC).strftime('%Y%m%dT%H%M%SZ')
        uid = f"{uuid.uuid4()}@events-mcp"
        # Basic RFC5545 VEVENT
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//events-mcp//EN",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{event.title.replace('',' ').strip()}",
            f"DESCRIPTION:{(event.snippet or event.url or '').replace('',' ')}",
            f"LOCATION:{(event.venue or event.location or '').replace('',' ')}",
            f"URL:{event.url}",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
        return "".join(lines) + ""
    except Exception:
        return None

def ensure_api_key():
    if not TAVILY_API_KEY:
        raise RuntimeError("Missing TAVILY_API_KEY environment variable")


def to_local_iso(dt: datetime, tz_name: str = DEFAULT_TIMEZONE) -> str:
    tzinfo = tz.gettz(tz_name) or tz.gettz("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    return dt.astimezone(tzinfo).isoformat()


def weekend_bounds(offset: int = 0, tz_name: str = DEFAULT_TIMEZONE) -> tuple[date, date]:
    # Find upcoming Saturday & Sunday for the given offset
    now_local = datetime.now(tz.gettz(tz_name)).date()
    # weekday(): Monday=0 ... Sunday=6
    days_until_sat = (5 - now_local.weekday()) % 7
    saturday = now_local + timedelta(days=days_until_sat + 7 * offset)
    sunday = saturday + timedelta(days=1)
    return saturday, sunday


def build_query(user_query: str, location: str, start: Optional[str], end: Optional[str]) -> str:
    parts = [user_query, location]
    if start and end:
        parts.append(f"{start}..{end}")
    elif start:
        parts.append(f"after {start}")
    # Add event keywords (lightly) to bias results
    parts.append("(" + " OR ".join(EVENT_KEYWORDS) + ")")
    return " ".join(p for p in parts if p)


def call_tavily(query: str, max_results: int = 20, include_domains: Optional[List[str]] = None, exclude_domains: Optional[List[str]] = None) -> Dict[str, Any]:
    ensure_api_key()
    search_depth = "advanced" if max_results > 10 else "basic"
    payload: Dict[str, Any] = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains
    with httpx.Client(timeout=httpx.Timeout(TAVILY_TIMEOUT)) as client:
        r = client.post(TAVILY_API_URL, json=payload)
        r.raise_for_status()
        return r.json()

# Best-effort extraction from Tavily results structure
DATE_PAT = re.compile(r"(\b\w{3,9}\s+\d{1,2},\s*\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b)")
TIME_PAT = re.compile(r"\b(\d{1,2}(:\d{2})?\s*(AM|PM|am|pm))\b")
VENUE_PAT = re.compile(r"at\s+([^.,\n]+)")


def parse_event_from_item(item: Dict[str, Any]) -> Event:
    title = item.get("title", "").strip()
    url = item.get("url", "")
    snippet = (item.get("content", "") or item.get("snippet", "")).strip()
    source = item.get("source", "")

    # naive extraction
    date_match = DATE_PAT.search(snippet)
    time_match = TIME_PAT.search(snippet)
    venue_match = VENUE_PAT.search(snippet)

    start_iso = None
    if date_match:
        try:
            dt_text = date_match.group(0)
            # If time exists, combine; else default to 19:00 local
            if time_match:
                dt_text = dt_text + " " + time_match.group(0)
            dt = isoparse(dt_text) if "T" in dt_text else isoparse(str(dt_text))
            start_iso = to_local_iso(dt)
        except Exception:
            start_iso = None

    venue = venue_match.group(1).strip() if venue_match else None

    return Event(
        title=title or "Untitled Event",
        url=url,
        start_datetime=start_iso,
        venue=venue,
        location=None,
        source=source,
        snippet=snippet or None,
    )


def normalize_results(tavily_json: Dict[str, Any]) -> List[Event]:
    items = tavily_json.get("results") or tavily_json.get("results", [])
    events: List[Event] = []
    for it in items or []:
        try:
            events.append(parse_event_from_item(it))
        except Exception:
            continue
    return events

# ---- Lu.ma parsing ----

def _jsonld_from_html(html: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        tree = HTMLParser(html)
        for node in tree.css('script[type="application/ld+json"]'):
            try:
                import json as _json
                raw = node.text(strip=True)
                if not raw:
                    continue
                data = _json.loads(raw)
                if isinstance(data, list):
                    out.extend(data)
                else:
                    out.append(data)
            except Exception:
                continue
    except Exception:
        pass
    return out


def _event_from_jsonld(obj: Dict[str, Any]) -> Optional[Event]:
    try:
        t = obj.get("@type")
        if isinstance(t, list):
            is_event = any(x.lower() == "event" for x in [str(v).lower() for v in t])
        else:
            is_event = str(t).lower() == "event"
        if not is_event:
            return None
        title = (obj.get("name") or obj.get("headline") or "").strip()
        url = obj.get("url") or ""
        start = obj.get("startDate") or obj.get("start_time")
        end = obj.get("endDate") or obj.get("end_time")
        loc = None
        venue_name = None
        loc_obj = obj.get("location")
        if isinstance(loc_obj, dict):
            venue_name = loc_obj.get("name")
            addr = loc_obj.get("address")
            if isinstance(addr, dict):
                parts = [addr.get("streetAddress"), addr.get("addressLocality"), addr.get("addressRegion"), addr.get("postalCode"), addr.get("addressCountry")]
                loc = ", ".join([p for p in parts if p])
        desc = obj.get("description") or None
        return Event(title=title or "Untitled Event", url=url, start_datetime=start, end_datetime=end, venue=venue_name, location=loc, snippet=desc)
    except Exception:
        return None


def parse_luma_page(html: str, page_url: str) -> List[Event]:
    events: List[Event] = []
    for js in _jsonld_from_html(html):
        ev = _event_from_jsonld(js)
        if ev:
            if not ev.url:
                ev.url = page_url
            events.append(ev)
        # also check @graph variants
        graph = js.get("@graph") if isinstance(js, dict) else None
        if isinstance(graph, list):
            for g in graph:
                ev2 = _event_from_jsonld(g) if isinstance(g, dict) else None
                if ev2:
                    if not ev2.url:
                        ev2.url = page_url
                    events.append(ev2)
    return events


def _host(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def _post_filter(events: List[Event], include: List[str], exclude: List[str], require_keywords: Optional[List[str]]) -> List[Event]:
    inc = [d.lower().lstrip(".") for d in (include or [])]
    exc = [d.lower().lstrip(".") for d in (exclude or [])]
    req = [w.lower() for w in (require_keywords or [])]

    def allowed(ev: Event) -> bool:
        h = _host(ev.url)
        if h:
            if exc and any(h.endswith(x) for x in exc):
                return False
            if inc and not any(h.endswith(x) for x in inc):
                return False
        if req:
            text = ((ev.title or "") + "" + (ev.snippet or "")).lower()
            if not any(w in text for w in req):
                return False
        return True

    return [e for e in events if allowed(e)]

def _ensure_datetime_with_default_time(d: datetime, default_hm: str) -> datetime:
    """If datetime has no time component (00:00) and came from a date-only parse,
    set HH:MM from default_hm (local tz)."""
    try:
        hh, mm = [int(x) for x in default_hm.split(":", 1)]
    except Exception:
        hh, mm = 19, 0
    return d.replace(hour=hh, minute=mm)


def _materialize_calendar(events: List[Event], duration_minutes: int, default_hm: str, drop_unparsed: bool, tz_name: str = DEFAULT_TIMEZONE) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for ev in events:
        start_iso = ev.start_datetime
        # If we only parsed a date (likely 00:00), ensure default time
        if start_iso:
            try:
                dt = isoparse(start_iso)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=tz.gettz(tz_name) or tz.UTC)
                # Heuristic: if midnight, assume date-only and apply default time
                if dt.hour == 0 and dt.minute == 0 and "T00:00" in start_iso:
                    dt = _ensure_datetime_with_default_time(dt, default_hm)
                end_dt = dt + timedelta(minutes=duration_minutes)
                start_iso = dt.isoformat()
                end_iso = end_dt.isoformat()
            except Exception:
                start_iso = None
                end_iso = None
        else:
            end_iso = None

        if not start_iso and drop_unparsed:
            continue

        out.append({
            "title": ev.title,
            "start": start_iso,
            "end": end_iso,
            "timezone": tz_name,
            "location": ev.venue or ev.location,
            "description": ev.snippet or ev.url,
            "url": ev.url,
        })
    return out

# -----------------------------
# MCP Server & Tools
# -----------------------------

mcp = FastMCP(
    name="events-discovery-agent",
    instructions=(
        "You are an events discovery assistant. You search the web via Tavily and "
        "return structured events. Prefer official calendars and trusted listings."
    ),
)


@mcp.tool()
async def search_events(args: SearchEventsArgs, ctx: Context | None = None) -> List[Event]:
    """Search for events between start_date and end_date near a location."""
    q = build_query(args.query, args.location, args.start_date, args.end_date)
    # domain biasing
    include = (args.include_domains or []) + (DEFAULT_INCLUDE_DOMAINS if args.use_default_domain_bias else [])
    exclude = (args.exclude_domains or []) + (DEFAULT_EXCLUDE_DOMAINS if args.use_default_domain_bias else [])
    # De-dup lists while preserving order
    def dedup(seq):
        seen = set(); out=[]
        for s in seq:
            if s and s not in seen:
                seen.add(s); out.append(s)
        return out
    include = dedup(include)
    exclude = dedup(exclude)

    data = call_tavily(q, max_results=args.max_results, include_domains=include or None, exclude_domains=exclude or None)
    events = normalize_results(data)
    # Server-side hard filter (domains/keywords) as safety net
    if 'include' in locals() and 'exclude' in locals():
        if getattr(args, 'hard_domain_filter', True):
            events = _post_filter(events, include, exclude, getattr(args, 'require_keywords', None))
    # Light post-filtering by date window if we managed to parse dates
    def in_window(ev: Event) -> bool:
        if not (args.start_date and args.end_date and ev.start_datetime):
            return True
        try:
            s = isoparse(ev.start_datetime).date()
            return (date.fromisoformat(args.start_date) <= s <= date.fromisoformat(args.end_date))
        except Exception:
            return True
    return [e for e in events if in_window(e)]


@mcp.tool()
async def weekend_guide(args: WeekendGuideArgs, ctx: Context | None = None) -> List[Event]:
    """Get a curated list of events for this (or next) weekend for given interests."""
    sat, sun = weekend_bounds(args.weekend_offset)
    interest_text = " ".join(args.interests or [])
    query = f"{interest_text} {args.location}"
    q = build_query(query, args.location, sat.isoformat(), sun.isoformat())
    include = (args.include_domains or []) + (DEFAULT_INCLUDE_DOMAINS if args.use_default_domain_bias else [])
    exclude = (args.exclude_domains or []) + (DEFAULT_EXCLUDE_DOMAINS if args.use_default_domain_bias else [])
    def dedup(seq):
        seen=set(); out=[]
        for s in seq:
            if s and s not in seen:
                seen.add(s); out.append(s)
        return out
    include = dedup(include)
    exclude = dedup(exclude)
    data = call_tavily(q, max_results=args.max_results, include_domains=include or None, exclude_domains=exclude or None)
    events = normalize_results(data)
    # Server-side hard filter (domains/keywords) as safety net
    if 'include' in locals() and 'exclude' in locals():
        if getattr(args, 'hard_domain_filter', True):
            events = _post_filter(events, include, exclude, getattr(args, 'require_keywords', None))
    if args.calendarize:
        for ev in events:
            ev.gcal_url = build_gcal_url(ev.title, ev.start_datetime, args.duration_minutes, ev.venue or ev.location, ev.snippet)
            ev.ics = build_ics(ev, args.duration_minutes)
    return events


@mcp.tool()
async def summarize_url(args: SummarizeUrlArgs, ctx: Context | None = None) -> Event:
    """Summarize a single URL and extract event-like info (best-effort)."""
    ensure_api_key()
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": args.url,
        "max_results": 1,
        "search_depth": "basic",
        "include_answer": False,
    }
    with httpx.Client(timeout=httpx.Timeout(TAVILY_TIMEOUT)) as client:
        r = client.post(TAVILY_API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
    items = data.get("results") or []
    if not items:
        return Event(title="No data", url=args.url)
    return parse_event_from_item(items[0])


@mcp.tool()
async def luma_scrape_url(args: LumaScrapeUrlArgs, ctx: Context | None = None) -> List[Event] | List[Dict[str, Any]]:
    """Fetch a Lu.ma event/collection page and parse JSON-LD Events directly."""
    with httpx.Client(timeout=httpx.Timeout(TAVILY_TIMEOUT)) as client:
        r = client.get(args.url, headers={"User-Agent": "events-mcp/1.0"})
        r.raise_for_status()
        html = r.text
    events = parse_luma_page(html, args.url)
    if args.calendar_ready:
        return _materialize_calendar(events, args.duration_minutes, args.default_start_time, args.drop_unparsed)
    return events


@mcp.tool()
async def luma_discover(args: LumaDiscoverArgs, ctx: Context | None = None) -> List[Event] | List[Dict[str, Any]]:
    """Use Tavily to discover Lu.ma URLs, then scrape each URL for JSON-LD Events."""
    # Discovery restricted to Lu.ma
    q = build_query(args.query, args.location, args.start_date, args.end_date)
    data = call_tavily(q, max_results=args.max_results, include_domains=["lu.ma"], exclude_domains=None)
    urls = []
    for it in (data.get("results") or []):
        u = it.get("url")
        if u and "lu.ma" in u:
            urls.append(u)
    # Fetch & parse
    out: List[Event] = []
    with httpx.Client(timeout=httpx.Timeout(TAVILY_TIMEOUT)) as client:
        for u in urls:
            try:
                r = client.get(u, headers={"User-Agent": "events-mcp/1.0"})
                if r.status_code != 200:
                    continue
                out.extend(parse_luma_page(r.text, u))
            except Exception:
                continue
    # Optionally calendarize
    if args.calendar_ready:
        return _materialize_calendar(out, args.duration_minutes, args.default_start_time, args.drop_unparsed)
    return out
    """Summarize a single URL and extract event-like info (best-effort)."""
    ensure_api_key()
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": args.url,
        "max_results": 1,
        "search_depth": "basic",
        "include_answer": False,
    }
    with httpx.Client(timeout=httpx.Timeout(TAVILY_TIMEOUT)) as client:
        r = client.post(TAVILY_API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
    items = data.get("results") or []
    if not items:
        return Event(title="No data", url=args.url)
    return parse_event_from_item(items[0])

# -----------------------------
# Entrypoint
# -----------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stdio", "http", "sse"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3002)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.mode == "stdio":
        mcp.run()
    elif args.mode == "http":
        # NOTE: some FastMCP versions don't accept 'debug' here
        mcp.run(transport="http", host=args.host, port=args.port)
    elif args.mode == "sse":
        # NOTE: some FastMCP versions don't accept 'debug' here
        mcp.run(transport="sse", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
    main()
