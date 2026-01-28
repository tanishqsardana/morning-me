# NYC Events MCP Server - Usage Examples

## Integration with Calendar Agent

The NYC Events MCP server is designed to work seamlessly with your Google Calendar MCP server. Here are practical examples of how they can work together:

### Example 1: Find Events Near a Meeting Location

**User Query:**
> "I have a meeting at Times Square tomorrow at 2pm. Find me a museum to visit nearby after 4pm."

**How it works:**
1. Calendar agent identifies the meeting location coordinates (40.7580, -73.9855)
2. Events MCP searches for nearby museums
3. Agent recommends events that fit the time window

**MCP Tool Call:**
```json
{
  "tool": "find_events_near_location",
  "arguments": {
    "latitude": 40.7580,
    "longitude": -73.9855,
    "radius_km": 2.0,
    "category": "museum",
    "start_date": "2025-10-21"
  }
}
```

### Example 2: Fill Free Time with Events

**User Query:**
> "I'm free next Tuesday evening. What music events are happening?"

**MCP Tool Call:**
```json
{
  "tool": "get_events_by_category",
  "arguments": {
    "category": "music",
    "start_date": "2025-10-28",
    "end_date": "2025-10-28",
    "limit": 10
  }
}
```

### Example 3: Plan a Day Around Events

**User Query:**
> "Show me all events happening on Halloween"

**MCP Tool Call:**
```json
{
  "tool": "get_events_by_date_range",
  "arguments": {
    "start_date": "2025-10-31",
    "end_date": "2025-10-31",
    "limit": 50
  }
}
```

### Example 4: Find Something Specific

**User Query:**
> "Are there any pop-up events near the MoMA this weekend?"

**MCP Tool Call:**
```json
{
  "tool": "find_events_near_location",
  "arguments": {
    "latitude": 40.7614,
    "longitude": -73.9776,
    "radius_km": 1.5,
    "category": "pop-ups",
    "start_date": "2025-10-25",
    "end_date": "2025-10-26"
  }
}
```

### Example 5: Browse by Category

**User Query:**
> "What movie screenings are available in the next week?"

**MCP Tool Call:**
```json
{
  "tool": "get_events_by_category",
  "arguments": {
    "category": "movies",
    "start_date": "2025-10-20",
    "end_date": "2025-10-27",
    "limit": 20
  }
}
```

### Example 6: Search by Venue or Keyword

**User Query:**
> "Are there any events at Bowery Ballroom?"

**MCP Tool Call:**
```json
{
  "tool": "search_events",
  "arguments": {
    "query": "Bowery Ballroom",
    "limit": 10
  }
}
```

## Common Coordinates for NYC Landmarks

Use these coordinates with `find_events_near_location`:

- **Times Square**: 40.7580, -73.9855
- **Central Park (center)**: 40.7829, -73.9654
- **MoMA**: 40.7614, -73.9776
- **Brooklyn Bridge**: 40.7061, -73.9969
- **Grand Central**: 40.7527, -73.9772
- **Empire State Building**: 40.7484, -73.9857
- **Chelsea Market**: 40.7424, -74.0061
- **Williamsburg**: 40.7081, -73.9571

## Integration Pattern with Calendar

When a user asks about events near their calendar appointments:

1. **Extract Calendar Event Location:**
   ```
   Calendar MCP → Get event details → Extract venue address
   Calendar MCP → Geocode address → Get lat/long
   ```

2. **Find Nearby Events:**
   ```
   Events MCP → find_events_near_location → Get events within radius
   ```

3. **Filter by Time:**
   ```
   Filter events that don't conflict with calendar appointments
   ```

4. **Present Options:**
   ```
   Show user events sorted by:
   - Distance from meeting location
   - Time compatibility
   - Category preference
   ```

## Best Practices

1. **Always specify date ranges** when possible to get more relevant results
2. **Use 2-3km radius** for proximity searches in Manhattan (venues are dense)
3. **Combine filters** for more specific results (category + date + location)
4. **Check event descriptions** for specific details about the events
5. **Use venue coordinates** from calendar events for accurate proximity search

## Tool Selection Guide

| User Intent | Best Tool |
|-------------|-----------|
| "Events near [location]" | `find_events_near_location` |
| "What's happening on [date]" | `get_events_by_date_range` |
| "Show me [category] events" | `get_events_by_category` |
| "Find [keyword]" | `search_events` |
| "Tell me about this event [ID]" | `get_event_by_id` |
| "What categories are available?" | `get_event_categories` |

## Sample Agent Conversation

```
User: I'm meeting someone at Chelsea Market for lunch tomorrow. 
      What can we do after, nearby?

Agent: Let me check what's happening near Chelsea Market tomorrow.

[Calls find_events_near_location with Chelsea Market coordinates]

Agent: Great! I found several events within 2km of Chelsea Market tomorrow:

1. 📅 Gallery Spotlight @ Whitney Museum
   Distance: 1.2 km
   Time: 2:00 PM - 5:00 PM
   
2. 📅 Indie Film Screening @ Angelika Film Center
   Distance: 0.8 km
   Time: 3:30 PM - 5:30 PM
   
3. 📅 Live Jazz @ Village Vanguard
   Distance: 1.5 km
   Time: 8:00 PM - 11:00 PM

Would you like me to add any of these to your calendar?
```

## Troubleshooting

### No events found?
- Check your date range (data only covers Oct 20 - Nov 20, 2025)
- Increase radius_km parameter
- Remove category filter to see all event types

### Too many results?
- Add category filter
- Narrow date range
- Reduce limit parameter
- Decrease radius for location searches



