from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# Price range enum for restaurant filtering
class PriceRange(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    UPSCALE = "upscale"


# Trip/flight enums
class TripType(str, Enum):
    ROUND_TRIP = "round_trip"
    ONE_WAY = "one_way"


class TravelClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


# Request models
class FlightRequest(BaseModel):
    origin: str = Field(description="Origin airport code or city (e.g., 'SFO', 'San Francisco')")
    destination: str = Field(description="Destination airport code or city (e.g., 'NRT', 'Tokyo')")
    departure_date: str = Field(description="Departure date in MM/DD/YYYY format")
    return_date: Optional[str] = Field(default=None, description="Return date in MM/DD/YYYY format (for round trip)")
    adults: int = Field(default=1, description="Number of adult passengers")
    travel_class: TravelClass = Field(default=TravelClass.ECONOMY, description="Travel class preference")


class HotelRequest(BaseModel):
    destination: str = Field(description="Destination city or location (e.g., 'Tokyo', 'Paris')")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format")
    adults: int = Field(default=2, description="Number of adult guests")
    rooms: int = Field(default=1, description="Number of rooms needed")


class ItineraryRequest(BaseModel):
    # Flight information
    trip_type: TripType = TripType.ROUND_TRIP
    from_city: str  # e.g., "SFO"
    to_city: str    # e.g., "NRT"
    departure_date: str  # Format: "MM/DD/YYYY"
    return_date: Optional[str] = None  # Format: "MM/DD/YYYY"
    adults: int = 1
    travel_class: TravelClass = TravelClass.ECONOMY

    # Travel interests and preferences
    interests: str  # Free text describing travel interests and preferences

    # Optional filters
    price_range: Optional[PriceRange] = None


# Demo models (kept if needed later)
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    is_active: bool = True

# Video Analysis models
class ActivityType(str, Enum):
    TRAVEL = "travel"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    EDUCATION = "education"
    SHOPPING = "shopping"
    OUTDOOR = "outdoor"
    CULTURAL = "cultural"
    BUSINESS = "business"
    OTHER = "other"


class VideoAnalysisRequest(BaseModel):
    video_url: str = Field(description="URL of the video to analyze (YouTube, TikTok, Instagram, Facebook, X/Twitter)")
    location: Optional[str] = Field(default=None, description="Optional location context for the activity")


class Activity(BaseModel):
    title: str = Field(description="Title or name of the activity")
    description: str = Field(description="Short description of the activity")
    activity_type: ActivityType = Field(description="Type/category of the activity")
    location: Optional[str] = Field(description="Location where the activity takes place")
    estimated_duration: Optional[int] = Field(description="Estimated time to complete the activity in minutes")
    confidence_score: float = Field(description="Confidence score of the activity detection (0.0 to 1.0)")


class VideoInfo(BaseModel):
    title: str
    platform: str
    uploader: str
    duration: Optional[int] = None
    url: str
    description: Optional[str] = None


class VideoAnalysisResponse(BaseModel):
    status: str
    video_info: VideoInfo
    activities: list[Activity]
    analysis_metadata: dict
    request_details: dict
