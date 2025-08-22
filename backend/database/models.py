"""
Pydantic Models for Convex Database Schema
Defines the normalized structure for all travel-related data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid


class Itinerary(BaseModel):
    """Parent itinerary record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    destination: str
    start_date: str
    end_date: str
    status: Literal["draft", "published", "archived"] = "draft"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ItineraryDay(BaseModel):
    """Individual day in an itinerary (normalized)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itinerary_id: str
    day_number: int
    date: str  # Format: "Day Name, Month Day" (e.g., "Monday, August 19")
    activities: List[str] = []  # List of activity IDs
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Activity(BaseModel):
    """Activity within a day"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itinerary_day_id: str
    title: str
    time: str  # HH:MM format
    duration: str  # Format: "Xh Ym" (e.g., "2h 30m")
    location: str
    activity_type: str  # flight, hotel, meal, activity, transport
    additional_info: str
    order: int  # For sorting activities within a day
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Flight(BaseModel):
    """Flight search result (top 3 by price)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itinerary_id: Optional[str] = None
    origin: str
    destination: str
    airline: str
    flight_number: Optional[str] = None
    departure_date: str
    arrival_date: Optional[str] = None
    price: float
    stops: int = 0
    duration: Optional[str] = None
    booking_url: Optional[str] = None
    travel_class: str = "economy"
    passengers: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Hotel(BaseModel):
    """Hotel search result (2 cheapest + 3 best rated)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itinerary_id: Optional[str] = None
    name: str
    address: str
    check_in_date: str
    check_out_date: str
    price: float
    rating: Optional[float] = None
    amenities: List[str] = []
    source: Literal["booking", "airbnb", "hotels.com"] = "booking"
    property_type: Optional[str] = None  # hotel, apartment, villa, etc.
    booking_url: Optional[str] = None
    image_url: Optional[str] = None
    reviews_count: Optional[int] = None
    room_type: Optional[str] = None
    guests: int = 2
    rooms: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Restaurant(BaseModel):
    """Restaurant recommendation (all, max 30)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    itinerary_id: Optional[str] = None
    name: str
    address: str
    cuisine: List[str]
    price_range: str  # $, $$, $$$, $$$$
    rating: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[str] = None
    status: Literal["found", "recommended", "visited"] = "found"
    source_url: Optional[str] = None
    description: Optional[str] = None
    reservation_required: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Job(BaseModel):
    """Background job tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # itinerary_generation, flight_search, hotel_search, etc.
    status: Literal[
        "pending", 
        "processing", 
        "searching_flights",
        "searching_hotels",
        "searching_restaurants",
        "generating_itinerary",
        "completed", 
        "failed"
    ] = "pending"
    progress: int = Field(default=0, ge=0, le=100)
    input: Optional[str] = None  # JSON string
    result: Optional[str] = None  # JSON string
    error: Optional[str] = None
    user_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())