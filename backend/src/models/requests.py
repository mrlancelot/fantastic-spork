"""Request Models - Clean Pydantic models for API request validation

All request models used by the TravelAI API endpoints.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

# ============================================================================
# TRAVEL SEARCH REQUESTS
# ============================================================================

class FlightSearchRequest(BaseModel):
    """Flight search request model"""
    origin: str = Field(..., description="Origin airport code or city")
    destination: str = Field(..., description="Destination airport code or city")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD) for round trips")
    adults: int = Field(1, ge=1, le=9, description="Number of adult passengers")
    seat_class: str = Field("economy", description="Seat class (economy, business, first)")
    
    @validator('seat_class')
    def validate_seat_class(cls, v):
        allowed = ['economy', 'business', 'first']
        if v.lower() not in allowed:
            raise ValueError(f'seat_class must be one of {allowed}')
        return v.lower()

class HotelSearchRequest(BaseModel):
    """Hotel search request model"""
    city_code: str = Field(..., description="City code (3 letters)")
    latitude: Optional[float] = Field(None, description="Latitude for location-based search")
    longitude: Optional[float] = Field(None, description="Longitude for location-based search")
    check_in_date: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out_date: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    adults: int = Field(1, ge=1, le=10, description="Number of adults")
    rooms: int = Field(1, ge=1, le=5, description="Number of rooms")

class ActivitySearchRequest(BaseModel):
    """Activity search request model"""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    radius: int = Field(20, ge=1, le=100, description="Search radius in kilometers")
    adults: int = Field(1, ge=1, le=20, description="Number of adults")

# ============================================================================
# AI & CHAT REQUESTS
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request for AI interactions"""
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class WeatherRequest(BaseModel):
    """Weather information request"""
    location: str = Field(..., description="Location name or coordinates")
    date: Optional[str] = Field(None, description="Date for weather forecast")

# ============================================================================
# USER MANAGEMENT REQUESTS
# ============================================================================

class StoreUserRequest(BaseModel):
    """Store user request from Clerk authentication"""
    clerk_user_id: str = Field(..., description="Clerk user ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User full name")
    image_url: Optional[str] = Field(None, description="User profile image URL")

# ============================================================================
# SMART PLANNER REQUESTS & MODELS
# ============================================================================

class DailySlot(BaseModel):
    """Daily slot model for itinerary planning"""
    id: Optional[str] = Field(None, description="Slot ID")
    time_slot: str = Field(..., description="Time slot (morning, midday, evening, night)")
    activity: str = Field(..., description="Activity name")
    description: str = Field(..., description="Activity description")
    duration: str = Field(..., description="Estimated duration")
    location: str = Field(..., description="Location")
    completed: bool = Field(False, description="Whether the slot is completed")
    booking_url: Optional[str] = Field("", description="Booking URL if applicable")
    notes: Optional[str] = Field("", description="User notes")
    
    @validator('time_slot')
    def validate_time_slot(cls, v):
        allowed = ['morning', 'midday', 'evening', 'night']
        if v.lower() not in allowed:
            raise ValueError(f'time_slot must be one of {allowed}')
        return v.lower()

class DailyPlan(BaseModel):
    """Daily plan model containing 4 slots + weather"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    slots: List[DailySlot] = Field(..., description="List of 4 daily slots")
    weather: Dict[str, Any] = Field(..., description="Weather information")
    
    @validator('slots')
    def validate_slots_count(cls, v):
        if len(v) != 4:
            raise ValueError('Each daily plan must have exactly 4 slots')
        return v

class SmartItinerary(BaseModel):
    """Complete smart itinerary model"""
    user_id: str = Field(..., description="User ID")
    destination: str = Field(..., description="Destination")
    start_date: str = Field(..., description="Trip start date")
    end_date: str = Field(..., description="Trip end date")
    travelers: int = Field(..., description="Number of travelers")
    daily_plans: List[DailyPlan] = Field(..., description="Daily plans")
    flights: List[Dict[str, Any]] = Field(default_factory=list, description="Flight bookings")
    hotels: List[Dict[str, Any]] = Field(default_factory=list, description="Hotel bookings")
    restaurants: List[Dict[str, Any]] = Field(default_factory=list, description="Restaurant reservations")
    travel_docs: List[Dict[str, Any]] = Field(default_factory=list, description="Travel documents")
    budget: Dict[str, Any] = Field(default_factory=dict, description="Budget information")
    group_members: List[str] = Field(default_factory=list, description="Group member IDs")

class SmartPlannerRequest(BaseModel):
    """Smart planner creation request"""
    destination: str = Field(..., description="Destination")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    travelers: int = Field(1, ge=1, le=20, description="Number of travelers")
    budget: Optional[int] = Field(None, description="Budget in USD")
    preferences: List[str] = Field(default_factory=list, description="Travel preferences")
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('end_date')
    def validate_end_after_start(cls, v, values):
        if 'start_date' in values:
            start = datetime.strptime(values['start_date'], '%Y-%m-%d')
            end = datetime.strptime(v, '%Y-%m-%d')
            if end <= start:
                raise ValueError('end_date must be after start_date')
        return v

# ============================================================================
# RESPONSE MODELS (for type hints and validation)
# ============================================================================

class APIResponse(BaseModel):
    """Standard API response model"""
    status: str = Field(..., description="Response status (success, error)")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error details")
    timestamp: Optional[str] = Field(None, description="Response timestamp")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field("healthy", description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Response timestamp")
