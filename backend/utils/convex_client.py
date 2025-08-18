"""
Convex Database Client for Python Backend
Handles all database operations with retry logic
"""

import os
import json
import time
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from convex import ConvexClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ConvexDB:
    def __init__(self):
        self.url = os.getenv("CONVEX_DEPLOYMENT_URL", "https://tough-armadillo-792.convex.cloud")
        self.client = ConvexClient(self.url)
        self.max_retries = 3
        self.retry_delay = 1
    def _retry_operation(self, operation, *args, **kwargs):
        """Execute operation with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")
                    raise e
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from data to avoid Convex validation errors"""
        cleaned = {}
        for key, value in data.items():
            if value is not None:
                cleaned[key] = value
        return cleaned
    def mutation(self, function_name: str, args: Dict[str, Any]) -> Any:
        """Execute a mutation (write operation)"""
        logger.info(f"Executing mutation: {function_name}")
        return self._retry_operation(self.client.mutation, function_name, args)
    def query(self, function_name: str, args: Dict[str, Any] = None) -> Any:
        """Execute a query (read operation)"""
        logger.info(f"Executing query: {function_name}")
        return self._retry_operation(self.client.query, function_name, args or {})

    def save_itinerary(self, data: Dict[str, Any]) -> str:
        """Save itinerary to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)
        data['updatedAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createItinerary", cleaned_data)
    def save_activity(self, data: Dict[str, Any]) -> str:
        """Save activity to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createActivity", cleaned_data)
    def save_flight(self, data: Dict[str, Any]) -> str:
        """Save flight to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)
        data['updatedAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createFlight", cleaned_data)
    def save_hotel(self, data: Dict[str, Any]) -> str:
        """Save hotel to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)
        data['updatedAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createHotel", cleaned_data)
    def save_restaurant(self, data: Dict[str, Any]) -> str:
        """Save restaurant to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)
        data['updatedAt'] = data.get('updatedAt', int(datetime.now().timestamp() * 1000))

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createRestaurant", cleaned_data)
    def save_job(self, data: Dict[str, Any]) -> str:
        """Save job to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)
        data['updatedAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createJob", cleaned_data)
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> None:
        """Update job status"""
        updates['updatedAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_updates = self._clean_data(updates)
        return self.mutation("mutations:updateJob", {"id": job_id, "updates": cleaned_updates})
    def save_user(self, data: Dict[str, Any]) -> str:
        """Save user to database"""
        data['createdAt'] = int(datetime.now().timestamp() * 1000)

        cleaned_data = self._clean_data(data)
        return self.mutation("mutations:createUser", cleaned_data)

    def save_multiple_activities(self, activities: List[Dict[str, Any]]) -> List[str]:
        """Save multiple activities"""
        ids = []
        for activity in activities:
            try:
                activity_id = self.save_activity(activity)
                ids.append(activity_id)
            except Exception as e:
                logger.error(f"Failed to save activity: {e}")
        return ids
    def save_multiple_flights(self, flights: List[Dict[str, Any]]) -> List[str]:
        """Save multiple flights"""
        ids = []
        for flight in flights:
            try:
                flight_id = self.save_flight(flight)
                ids.append(flight_id)
            except Exception as e:
                logger.error(f"Failed to save flight: {e}")
        return ids
    def save_multiple_hotels(self, hotels: List[Dict[str, Any]]) -> List[str]:
        """Save multiple hotels"""
        ids = []
        for hotel in hotels:
            try:
                hotel_id = self.save_hotel(hotel)
                ids.append(hotel_id)
            except Exception as e:
                logger.error(f"Failed to save hotel: {e}")
        return ids
    def save_multiple_restaurants(self, restaurants: List[Dict[str, Any]]) -> List[str]:
        """Save multiple restaurants"""
        ids = []
        for restaurant in restaurants:
            try:
                restaurant_id = self.save_restaurant(restaurant)
                ids.append(restaurant_id)
            except Exception as e:
                logger.error(f"Failed to save restaurant: {e}")
        return ids



_db_instance = None

def get_db() -> ConvexDB:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ConvexDB()
    return _db_instance
