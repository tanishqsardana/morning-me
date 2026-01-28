"""
EventsService - Database operations for NYC events.
Handles SQLite queries and proximity calculations.
"""

import sqlite3
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import math

logger = logging.getLogger("nyc-events-mcp")


class EventsService:
    """
    Service class for querying the NYC events database.
    Provides methods for searching, filtering, and proximity-based queries.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the events service.
        
        Args:
            db_path: Path to the SQLite database. If None, defaults to workspace path.
        """
        if db_path is None:
            # Default to the database in the workspace root
            # Navigate from src/nyc_events_mcp/tools/events_service.py -> workspace root
            current_dir = os.path.dirname(os.path.abspath(__file__))  # tools/
            src_dir = os.path.dirname(current_dir)  # nyc_events_mcp/
            pkg_dir = os.path.dirname(src_dir)  # src/
            server_dir = os.path.dirname(pkg_dir)  # nyc_events_mcp/
            workspace_root = os.path.dirname(server_dir)  # morning_me/
            db_path = os.path.join(workspace_root, "events_oct20_to_nov20_2025_nyc.sqlite")
        
        self.db_path = db_path
        logger.info(f"EventsService initialized with database: {self.db_path}")
        
        # Verify database exists
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Events database not found at: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert a database row to a dictionary.
        
        Args:
            row: SQLite Row object
            
        Returns:
            Dictionary representation of the row
        """
        return {
            "event_id": row["event_id"],
            "title": row["title"],
            "category": row["category"],
            "date": row["date"],
            "start_time_local": row["start_time_local"],
            "end_time_local": row["end_time_local"],
            "venue_name": row["venue_name"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "description": row["description"]
        }
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two coordinates using the Haversine formula.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers
        """
        # Radius of Earth in kilometers
        R = 6371.0
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    async def search_events(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for events with various filters.
        
        Args:
            query: Search query for title, description, or venue
            category: Filter by category (music, museum, pop-ups, football, movies)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of results to return
            
        Returns:
            List of event dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR description LIKE ? OR venue_name LIKE ?)"
            search_pattern = f"%{query}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if category:
            sql += " AND category = ?"
            params.append(category.lower())
        
        if start_date:
            sql += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            sql += " AND date <= ?"
            params.append(end_date)
        
        sql += " ORDER BY date, start_time_local LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        events = [self._row_to_dict(row) for row in rows]
        logger.info(f"Found {len(events)} events matching search criteria")
        return events
    
    async def get_events_by_category(
        self,
        category: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get events by category.
        
        Args:
            category: Event category (music, museum, pop-ups, football, movies)
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results
            
        Returns:
            List of event dictionaries
        """
        return await self.search_events(
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    async def get_events_by_date_range(
        self,
        start_date: str,
        end_date: str,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get events within a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of event dictionaries
        """
        return await self.search_events(
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit
        )
    
    async def find_events_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 2.0,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find events near a specific location using proximity search.
        
        Args:
            latitude: Latitude of the reference location
            longitude: Longitude of the reference location
            radius_km: Search radius in kilometers (default 2km)
            category: Optional category filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results
            
        Returns:
            List of event dictionaries with distance information, sorted by distance
        """
        # First get all potentially matching events
        events = await self.search_events(
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # Get more to filter by distance
        )
        
        # Calculate distances and filter
        events_with_distance = []
        for event in events:
            distance = self.calculate_distance(
                latitude, longitude,
                event["latitude"], event["longitude"]
            )
            
            if distance <= radius_km:
                event["distance_km"] = round(distance, 2)
                event["distance_miles"] = round(distance * 0.621371, 2)
                events_with_distance.append(event)
        
        # Sort by distance
        events_with_distance.sort(key=lambda x: x["distance_km"])
        
        # Return limited results
        results = events_with_distance[:limit]
        logger.info(f"Found {len(results)} events within {radius_km}km of location")
        return results
    
    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: The unique event identifier
            
        Returns:
            Event dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    async def get_all_categories(self) -> List[str]:
        """
        Get list of all available event categories.
        
        Returns:
            List of category names
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM events ORDER BY category")
        rows = cursor.fetchall()
        conn.close()
        
        categories = [row["category"] for row in rows]
        return categories
    
    def format_event_summary(self, event: Dict[str, Any]) -> str:
        """
        Format an event as a human-readable summary.
        
        Args:
            event: Event dictionary
            
        Returns:
            Formatted string representation
        """
        lines = [
            f"📅 {event['title']}",
            f"   Category: {event['category'].title()}",
            f"   Date: {event['date']}",
            f"   Time: {event['start_time_local'].split('T')[1]} - {event['end_time_local'].split('T')[1]}",
            f"   Venue: {event['venue_name']}",
            f"   Location: ({event['latitude']}, {event['longitude']})"
        ]
        
        if "distance_km" in event:
            lines.append(f"   Distance: {event['distance_km']} km ({event['distance_miles']} miles)")
        
        if event.get("description"):
            lines.append(f"   Description: {event['description']}")
        
        lines.append(f"   Event ID: {event['event_id']}")
        
        return "\n".join(lines)
    
    def format_events_list(self, events: List[Dict[str, Any]]) -> str:
        """
        Format a list of events as a human-readable summary.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Formatted string representation
        """
        if not events:
            return "No events found."
        
        lines = [f"Found {len(events)} event(s):\n"]
        
        for i, event in enumerate(events, 1):
            lines.append(f"\n{i}. {self.format_event_summary(event)}")
        
        return "\n".join(lines)

