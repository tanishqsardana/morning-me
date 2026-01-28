"""
Demo script showing the NYC Events MCP Server capabilities.
Run this to see example queries and results.
"""

import sys
import asyncio

sys.path.insert(0, 'src')

from nyc_events_mcp.tools.events_service import EventsService


async def demo():
    """Demonstrate the NYC Events MCP Server capabilities."""
    
    print("\n" + "="*80)
    print("NYC EVENTS MCP SERVER - DEMONSTRATION")
    print("="*80)
    
    es = EventsService()
    
    # Demo 1: Find events near a calendar meeting location
    print("\n📍 DEMO 1: Find events near Times Square (Calendar Integration Use Case)")
    print("-" * 80)
    print("Scenario: You have a meeting at Times Square at 2pm.")
    print("Looking for events within 2km...")
    print()
    
    nearby = await es.find_events_near_location(
        latitude=40.7580,
        longitude=-73.9855,
        radius_km=2.0,
        limit=3
    )
    
    for i, event in enumerate(nearby, 1):
        print(f"{i}. {event['title']}")
        print(f"   📍 {event['venue_name']} ({event['distance_km']}km away)")
        print(f"   🕒 {event['start_time_local'].split('T')[1]} - {event['end_time_local'].split('T')[1]}")
        print(f"   📅 {event['date']}")
        print()
    
    # Demo 2: Browse by category
    print("\n🎭 DEMO 2: Browse Museum Events")
    print("-" * 80)
    museums = await es.get_events_by_category("museum", limit=3)
    
    for i, event in enumerate(museums, 1):
        print(f"{i}. {event['title']}")
        print(f"   📍 {event['venue_name']}")
        print(f"   📅 {event['date']} at {event['start_time_local'].split('T')[1]}")
        print()
    
    # Demo 3: Search by keyword
    print("\n🔍 DEMO 3: Search for 'Gallery' Events")
    print("-" * 80)
    gallery = await es.search_events(query="Gallery", limit=3)
    
    for i, event in enumerate(gallery, 1):
        print(f"{i}. {event['title']}")
        print(f"   📍 {event['venue_name']}")
        print(f"   📅 {event['date']}")
        print()
    
    # Demo 4: Find events on a specific date
    print("\n📅 DEMO 4: Events on October 25, 2025")
    print("-" * 80)
    specific_date = await es.get_events_by_date_range(
        start_date="2025-10-25",
        end_date="2025-10-25",
        limit=5
    )
    
    categories = {}
    for event in specific_date:
        cat = event['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(event)
    
    for category, events in categories.items():
        print(f"\n{category.upper()}:")
        for event in events:
            print(f"  • {event['title']} at {event['venue_name']}")
    
    # Demo 5: Integration scenario
    print("\n\n🤝 DEMO 5: Calendar + Events Integration Scenario")
    print("-" * 80)
    print("Scenario: User asks 'I have lunch at Chelsea Market tomorrow.")
    print("          What pop-up events are nearby?'")
    print()
    print("Step 1: Calendar MCP provides Chelsea Market coordinates")
    print("        → (40.7424, -74.0061)")
    print()
    print("Step 2: Events MCP finds nearby pop-ups...")
    print()
    
    popup_nearby = await es.find_events_near_location(
        latitude=40.7424,
        longitude=-74.0061,
        radius_km=1.5,
        category="pop-ups",
        limit=3
    )
    
    if popup_nearby:
        print(f"Found {len(popup_nearby)} pop-up event(s) within 1.5km:")
        for i, event in enumerate(popup_nearby, 1):
            print(f"\n{i}. {event['title']}")
            print(f"   📍 {event['venue_name']}")
            print(f"   🚶 {event['distance_km']}km ({event['distance_miles']} miles) away")
            print(f"   🕒 {event['start_time_local'].split('T')[1]} - {event['end_time_local'].split('T')[1]}")
            print(f"   📅 {event['date']}")
    else:
        print("No pop-up events found within 1.5km. Try increasing the radius!")
    
    # Statistics
    print("\n\n📊 DATABASE STATISTICS")
    print("-" * 80)
    categories = await es.get_all_categories()
    print(f"Categories: {', '.join(categories)}")
    
    all_events = await es.search_events(limit=1000)
    print(f"Total events: {len(all_events)}")
    
    # Date range
    if all_events:
        dates = sorted(set(e['date'] for e in all_events))
        print(f"Date range: {dates[0]} to {dates[-1]}")
    
    print("\n" + "="*80)
    print("DEMO COMPLETE!")
    print("="*80)
    print("\nTo use this in Claude Desktop:")
    print("1. Add the server to your Claude Desktop config")
    print("2. Restart Claude Desktop")
    print("3. Ask questions like:")
    print("   • 'Find music events near Times Square'")
    print("   • 'What museums can I visit this weekend?'")
    print("   • 'Show me events on Halloween'")
    print("\nSee QUICKSTART.md for setup instructions!")
    print()


if __name__ == "__main__":
    asyncio.run(demo())



