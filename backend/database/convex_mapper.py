"""
Mapper functions to convert Python models to Convex schema format
Maps between our normalized models and existing Convex table schemas
"""

from typing import Dict, Any, Optional
from datetime import datetime


def to_convex_flight(flight_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python Flight model to Convex flights table schema
    
    Convex schema expects:
    - userId (string, required)
    - origin, destination, airline, flightNumber (strings)
    - departureDate, returnDate (strings)
    - price (number), currency (string)
    - stops (number), duration (string)
    - status (searching/booked/cancelled/completed)
    - createdAt, updatedAt (timestamps as numbers)
    """
    return {
        "userId": flight_data.get("user_id", "system"),
        "origin": flight_data.get("origin", ""),
        "destination": flight_data.get("destination", ""),
        "airline": flight_data.get("airline", ""),
        "flightNumber": flight_data.get("flight_number", ""),
        "departureDate": flight_data.get("departure_date", ""),
        "returnDate": flight_data.get("arrival_date"),  # Map arrival to return
        "price": float(flight_data.get("price", 0)),
        "currency": "USD",  # Default currency
        "stops": int(flight_data.get("stops", 0)),
        "duration": flight_data.get("duration", ""),
        "status": "searching",  # Default status
        "createdAt": int(datetime.now().timestamp() * 1000),  # Milliseconds
        "updatedAt": int(datetime.now().timestamp() * 1000),
    }


def to_convex_hotel(hotel_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python Hotel model to Convex hotels table schema
    
    Convex schema expects:
    - userId (string, required)
    - name, address, city, country (strings)
    - checkInDate, checkOutDate (strings)
    - price (number), currency (string)
    - rating (number, optional)
    - status (searching/booked/cancelled/completed)
    - createdAt, updatedAt (timestamps as numbers)
    """
    # Handle optional rating - Convex doesn't accept None for numbers
    rating = hotel_data.get("rating")
    if rating is not None:
        rating = float(rating)
    else:
        rating = 0.0  # Default to 0 instead of None
    
    return {
        "userId": hotel_data.get("user_id", "system"),
        "name": hotel_data.get("name", ""),
        "address": hotel_data.get("address", ""),
        "city": hotel_data.get("address", "").split(",")[0] if hotel_data.get("address") else "",
        "country": "USA",  # Default country
        "checkInDate": hotel_data.get("check_in_date", ""),
        "checkOutDate": hotel_data.get("check_out_date", ""),
        "price": float(hotel_data.get("price", 0)),
        "currency": "USD",
        "rating": rating,
        "status": "searching",
        "createdAt": int(datetime.now().timestamp() * 1000),
        "updatedAt": int(datetime.now().timestamp() * 1000),
    }


def to_convex_restaurant(restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Restaurant data received: {restaurant_data}")
    """
    Convert Python Restaurant model to Convex restaurants table schema
    
    Convex schema expects:
    - name, address, city (strings, required)
    - cuisine (array of strings, optional)
    - priceRange (string, optional)
    - rating (number, optional)
    - phone, website, hours, description (strings, optional)
    - createdAt, updatedAt (timestamps as numbers)
    """
    # Handle optional rating - Convex doesn't accept None for numbers
    rating = restaurant_data.get("rating")
    if rating is not None:
        rating = float(rating)
    else:
        rating = 0.0  # Default to 0 instead of None
    
    # Ensure all string fields are not None
    phone = restaurant_data.get("phone")
    if phone is None:
        phone = ""
    
    website = restaurant_data.get("website")
    if website is None:
        website = ""
    
    hours = restaurant_data.get("hours")
    if hours is None:
        hours = ""
    
    description = restaurant_data.get("description")
    if description is None:
        description = ""
    
    return {
        "userId": restaurant_data.get("user_id", "system"),
        "name": restaurant_data.get("name", ""),
        "address": restaurant_data.get("address", ""),
        "city": restaurant_data.get("address", "").split(",")[0] if restaurant_data.get("address") else "",
        "cuisine": restaurant_data.get("cuisine") or [],
        "priceRange": restaurant_data.get("price_range", "$$"),
        "rating": rating,
        "phone": phone,
        "website": website,
        "hours": hours,
        "description": description,
        "createdAt": int(datetime.now().timestamp() * 1000),
        "updatedAt": int(datetime.now().timestamp() * 1000),
    }


def to_convex_itinerary(itinerary_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python Itinerary model to Convex itineraries table schema
    
    Convex schema expects:
    - userId (string, optional but can't be null)
    - destination, startDate, endDate (strings)
    - status (draft/published/archived)
    - interests (array of strings, optional)
    - budget (number, optional)
    - data (any, optional - for storing full itinerary JSON)
    - createdAt, updatedAt (timestamps as numbers)
    """
    # Handle userId - must be a string, not None
    user_id = itinerary_data.get("user_id")
    if user_id is None:
        user_id = "system"
    
    # Handle budget - must be a number or not included
    budget = itinerary_data.get("budget")
    if budget is not None:
        budget = float(budget)
    
    result = {
        "destination": itinerary_data.get("destination", ""),
        "startDate": itinerary_data.get("start_date", ""),
        "endDate": itinerary_data.get("end_date", ""),
        "status": itinerary_data.get("status", "draft"),
        "interests": itinerary_data.get("interests") or [],
        "createdAt": int(datetime.now().timestamp() * 1000),
        "updatedAt": int(datetime.now().timestamp() * 1000),
    }
    
    # Only add optional fields if they have values
    if user_id:
        result["userId"] = user_id
    if budget is not None:
        result["budget"] = budget
    if itinerary_data.get("data") is not None:
        result["data"] = itinerary_data.get("data")
    
    return result


def to_convex_itinerary_day(day_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python ItineraryDay model to Convex itinerary_days table schema
    
    Convex schema expects:
    - itineraryId (id reference to itineraries table) 
    - dayNumber (number)
    - date (string)
    - createdAt, updatedAt (timestamps as numbers)
    
    NOTE: itineraryId will be overridden with Convex ID in repository
    """
    return {
        # Don't include itineraryId here - it will be set in repository with Convex ID
        "dayNumber": int(day_data.get("day_number", 1)),
        "date": day_data.get("date", ""),
        "createdAt": int(datetime.now().timestamp() * 1000),
        "updatedAt": int(datetime.now().timestamp() * 1000),
    }


def to_convex_activity(activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python Activity model to Convex activities table schema
    
    Convex schema expects:
    - itineraryId (id reference to itineraries table)
    - itineraryDayId (optional id reference to itinerary_days table)
    - day (number)
    - time (string)
    - title (string)
    - description (optional string)
    - location (optional string)
    - duration (optional number in minutes)
    - type (optional string)
    - createdAt (timestamp as number)
    """
    # Handle duration conversion (might be string or number)
    duration = activity_data.get("duration")
    if duration and isinstance(duration, str):
        # Try to extract number from string like "120 minutes"
        try:
            duration = int(duration.split()[0]) if duration else None
        except:
            duration = None
    
    result = {
        "itineraryId": activity_data.get("itinerary_id", ""),
        "itineraryDayId": activity_data.get("itinerary_day_id"),
        "day": int(activity_data.get("day", 1)),
        "time": activity_data.get("time", ""),
        "title": activity_data.get("title", ""),
        "description": activity_data.get("description", ""),
        "location": activity_data.get("location", ""),
        "type": activity_data.get("activity_type", ""),
        "createdAt": int(datetime.now().timestamp() * 1000),
    }
    
    # Only include duration if it has a valid value
    if duration:
        result["duration"] = int(duration)
    
    return result


def to_convex_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python Job model to Convex jobs table schema
    
    Convex schema expects:
    - type (string, required)
    - status (pending/processing/completed/failed)
    - payload, result (any, optional)
    - error (string, optional)
    - userId (string, optional)
    - createdAt, updatedAt (timestamps as numbers)
    """
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Job data before conversion: {job_data}")
    
    # Handle None values explicitly
    error = job_data.get("error")
    if error is None:
        error = ""
    
    user_id = job_data.get("user_id")
    if user_id is None:
        user_id = ""
    
    result = {
        "id": job_data.get("id", ""),  # String ID for backend reference (now required)
        "type": job_data.get("type", ""),
        "status": job_data.get("status", "pending"),
        "payload": job_data.get("input"),  # Map input to payload
        "result": job_data.get("result"),
        "error": error,
        "userId": user_id,
        "retryCount": 0,
        "maxRetries": 3,
        "createdAt": int(datetime.now().timestamp() * 1000),
        "updatedAt": int(datetime.now().timestamp() * 1000),
    }
    
    logger.debug(f"Job data after conversion: {result}")
    return result