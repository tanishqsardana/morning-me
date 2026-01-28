"""
Event-related tool handlers for the NYC Events MCP server.
This module contains all event-specific tool implementations.
"""

import json
import logging
from collections.abc import Sequence
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from .toolhandler import ToolHandler
from .events_service import EventsService

logger = logging.getLogger("nyc-events-mcp")


class SearchEventsToolHandler(ToolHandler):
    """
    Tool handler for searching events with various filters.
    """
    
    def __init__(self):
        super().__init__("search_events")
        self.events_service = EventsService()
    
    def get_tool_description(self) -> Tool:
        """
        Return the tool description for event search.
        """
        return Tool(
            name=self.name,
            description="""Search for NYC events with optional filters. You can search by keywords in the title, 
            description, or venue name. You can also filter by category, date range, or a combination of these. 
            This is a flexible search tool that returns events matching your criteria.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to match against event title, description, or venue name (optional)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by event category: music, museum, pop-ups, football, or movies (optional)",
                        "enum": ["music", "museum", "pop-ups", "football", "movies"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (optional, e.g., '2025-10-20')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (optional, e.g., '2025-11-20')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        )
    
    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """
        Execute the search events tool.
        """
        try:
            query = args.get("query")
            category = args.get("category")
            start_date = args.get("start_date")
            end_date = args.get("end_date")
            limit = args.get("limit", 20)
            
            logger.info(f"Searching events with query={query}, category={category}, dates={start_date} to {end_date}")
            
            # Get events from service
            events = await self.events_service.search_events(
                query=query,
                category=category,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Format the response
            formatted_response = self.events_service.format_events_list(events)
            
            return [
                TextContent(
                    type="text",
                    text=formatted_response
                )
            ]
            
        except Exception as e:
            logger.exception(f"Error in search_events: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"Error searching events: {str(e)}"
                )
            ]


class GetEventsByCategoryToolHandler(ToolHandler):
    """
    Tool handler for getting events by category.
    """
    
    def __init__(self):
        super().__init__("get_events_by_category")
        self.events_service = EventsService()
    
    def get_tool_description(self) -> Tool:
        """
        Return the tool description for category-based event retrieval.
        """
        return Tool(
            name=self.name,
            description="""Get NYC events filtered by category. Available categories are: music, museum, pop-ups, 
            football, and movies. You can optionally filter by date range as well. This is useful when you want 
            to explore all events in a specific category.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Event category to filter by",
                        "enum": ["music", "museum", "pop-ups", "football", "movies"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional start date in YYYY-MM-DD format (e.g., '2025-10-20')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional end date in YYYY-MM-DD format (e.g., '2025-11-20')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20
                    }
                },
                "required": ["category"]
            }
        )
    
    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """
        Execute the get events by category tool.
        """
        try:
            self.validate_required_args(args, ["category"])
            
            category = args["category"]
            start_date = args.get("start_date")
            end_date = args.get("end_date")
            limit = args.get("limit", 20)
            
            logger.info(f"Getting {category} events from {start_date} to {end_date}")
            
            # Get events from service
            events = await self.events_service.get_events_by_category(
                category=category,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Format the response
            formatted_response = self.events_service.format_events_list(events)
            
            return [
                TextContent(
                    type="text",
                    text=formatted_response
                )
            ]
            
        except Exception as e:
            logger.exception(f"Error in get_events_by_category: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"Error getting events by category: {str(e)}"
                )
            ]


class GetEventsByDateRangeToolHandler(ToolHandler):
    """
    Tool handler for getting events within a date range.
    """
    
    def __init__(self):
        super().__init__("get_events_by_date_range")
        self.events_service = EventsService()
    
    def get_tool_description(self) -> Tool:
        """
        Return the tool description for date range event retrieval.
        """
        return Tool(
            name=self.name,
            description="""Get NYC events within a specific date range. This is useful when you want to see 
            what's happening during a particular time period. You can optionally filter by category as well. 
            Events are returned in chronological order.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (e.g., '2025-10-20')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (e.g., '2025-11-20')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: music, museum, pop-ups, football, or movies",
                        "enum": ["music", "museum", "pop-ups", "football", "movies"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50)",
                        "default": 50
                    }
                },
                "required": ["start_date", "end_date"]
            }
        )
    
    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """
        Execute the get events by date range tool.
        """
        try:
            self.validate_required_args(args, ["start_date", "end_date"])
            
            start_date = args["start_date"]
            end_date = args["end_date"]
            category = args.get("category")
            limit = args.get("limit", 50)
            
            logger.info(f"Getting events from {start_date} to {end_date}, category={category}")
            
            # Get events from service
            events = await self.events_service.get_events_by_date_range(
                start_date=start_date,
                end_date=end_date,
                category=category,
                limit=limit
            )
            
            # Format the response
            formatted_response = self.events_service.format_events_list(events)
            
            return [
                TextContent(
                    type="text",
                    text=formatted_response
                )
            ]
            
        except Exception as e:
            logger.exception(f"Error in get_events_by_date_range: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"Error getting events by date range: {str(e)}"
                )
            ]


class FindEventsNearLocationToolHandler(ToolHandler):
    """
    Tool handler for finding events near a specific location (proximity search).
    """
    
    def __init__(self):
        super().__init__("find_events_near_location")
        self.events_service = EventsService()
    
    def get_tool_description(self) -> Tool:
        """
        Return the tool description for proximity-based event search.
        """
        return Tool(
            name=self.name,
            description="""Find NYC events near a specific location using latitude and longitude coordinates. 
            This is perfect for finding events close to another calendar event or a specific address. 
            Results include distance information and are sorted by proximity. You can specify a search radius 
            in kilometers (default 2km). This tool is especially useful when integrated with a calendar to find 
            events near scheduled appointments.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of the reference location (e.g., 40.7580 for Times Square)"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of the reference location (e.g., -73.9855 for Times Square)"
                    },
                    "radius_km": {
                        "type": "number",
                        "description": "Search radius in kilometers (default: 2.0)",
                        "default": 2.0
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: music, museum, pop-ups, football, or movies",
                        "enum": ["music", "museum", "pop-ups", "football", "movies"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional start date in YYYY-MM-DD format (e.g., '2025-10-20')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional end date in YYYY-MM-DD format (e.g., '2025-11-20')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20
                    }
                },
                "required": ["latitude", "longitude"]
            }
        )
    
    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """
        Execute the find events near location tool.
        """
        try:
            self.validate_required_args(args, ["latitude", "longitude"])
            
            latitude = args["latitude"]
            longitude = args["longitude"]
            radius_km = args.get("radius_km", 2.0)
            category = args.get("category")
            start_date = args.get("start_date")
            end_date = args.get("end_date")
            limit = args.get("limit", 20)
            
            logger.info(f"Finding events near ({latitude}, {longitude}) within {radius_km}km")
            
            # Get events from service
            events = await self.events_service.find_events_near_location(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                category=category,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Format the response with distance info
            if events:
                response_text = f"Found {len(events)} event(s) within {radius_km}km:\n"
                for i, event in enumerate(events, 1):
                    response_text += f"\n{i}. " + self.events_service.format_event_summary(event) + "\n"
            else:
                response_text = f"No events found within {radius_km}km of the specified location."
            
            return [
                TextContent(
                    type="text",
                    text=response_text
                )
            ]
            
        except Exception as e:
            logger.exception(f"Error in find_events_near_location: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"Error finding events near location: {str(e)}"
                )
            ]


class GetEventByIdToolHandler(ToolHandler):
    """
    Tool handler for getting a specific event by its ID.
    """
    
    def __init__(self):
        super().__init__("get_event_by_id")
        self.events_service = EventsService()
    
    def get_tool_description(self) -> Tool:
        """
        Return the tool description for getting an event by ID.
        """
        return Tool(
            name=self.name,
            description="""Get detailed information about a specific NYC event using its unique event ID. 
            This is useful when you have an event ID from a previous search and want to retrieve full details.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The unique identifier of the event (UUID format)"
                    }
                },
                "required": ["event_id"]
            }
        )
    
    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """
        Execute the get event by ID tool.
        """
        try:
            self.validate_required_args(args, ["event_id"])
            
            event_id = args["event_id"]
            
            logger.info(f"Getting event with ID: {event_id}")
            
            # Get event from service
            event = await self.events_service.get_event_by_id(event_id)
            
            if event:
                formatted_response = self.events_service.format_event_summary(event)
            else:
                formatted_response = f"Event not found with ID: {event_id}"
            
            return [
                TextContent(
                    type="text",
                    text=formatted_response
                )
            ]
            
        except Exception as e:
            logger.exception(f"Error in get_event_by_id: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"Error getting event by ID: {str(e)}"
                )
            ]


class GetEventCategoriesToolHandler(ToolHandler):
    """
    Tool handler for listing all available event categories.
    """
    
    def __init__(self):
        super().__init__("get_event_categories")
        self.events_service = EventsService()
    
    def get_tool_description(self) -> Tool:
        """
        Return the tool description for listing categories.
        """
        return Tool(
            name=self.name,
            description="""Get a list of all available event categories in the NYC events database. 
            This helps you understand what types of events are available.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    
    async def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """
        Execute the get event categories tool.
        """
        try:
            logger.info("Getting all event categories")
            
            # Get categories from service
            categories = await self.events_service.get_all_categories()
            
            response_text = "Available event categories:\n\n"
            for cat in categories:
                response_text += f"- {cat}\n"
            
            return [
                TextContent(
                    type="text",
                    text=response_text
                )
            ]
            
        except Exception as e:
            logger.exception(f"Error in get_event_categories: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"Error getting event categories: {str(e)}"
                )
            ]


