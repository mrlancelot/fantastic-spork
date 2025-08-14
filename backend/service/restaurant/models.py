"""Models for restaurant service"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserPreferences(BaseModel):
    """User preferences for restaurant search"""
    # Required fields
    city: str = Field(description="City to search in")
    
    # Optional fields with defaults
    country: str = Field(default="", description="Country code (auto-detected if empty)")
    food_type: str = Field(default="restaurant", description="Type of food/cuisine")
    party_size: int = Field(default=2, ge=1, le=20, description="Number of people")
    budget_level: Optional[str] = Field(default="$$", description="Budget: $, $$, $$$, $$$$")
    
    # Optional preferences
    occasion: Optional[str] = Field(default=None, description="Special occasion")
    time: Optional[str] = Field(default=None, description="Meal time")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")
    allergies: List[str] = Field(default_factory=list, description="Food allergies")
    preferred_ambiance: List[str] = Field(default_factory=list, description="Preferred ambiance")
    must_have: List[str] = Field(default_factory=list, description="Must-have features")
    avoid: List[str] = Field(default_factory=list, description="Things to avoid")
    special_requirements: List[str] = Field(default_factory=list, description="Special requirements")

class Restaurant(BaseModel):
    """Restaurant information"""
    name: str = Field(description="Restaurant name")
    
    # Basic info
    address: Optional[str] = Field(default=None, description="Restaurant address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="Rating (0-5)")
    price_level: Optional[str] = Field(default=None, description="Price level ($-$$$$)")
    hours: Optional[str] = Field(default=None, description="Operating hours")
    
    # Description and sources
    description: Optional[str] = Field(default=None, description="Restaurant description")
    source_urls: List[str] = Field(default_factory=list, description="Source URLs")
    image_urls: List[str] = Field(default_factory=list, description="Image URLs")
    
    # LLM-generated insights
    match_score: Optional[float] = Field(default=None, ge=0, le=10, description="Match score (0-10)")
    authenticity_score: Optional[float] = Field(default=None, ge=0, le=10, description="Authenticity score (0-10)")
    why_recommended: Optional[str] = Field(default=None, description="Why this restaurant is recommended")
    potential_concerns: List[str] = Field(default_factory=list, description="Potential concerns")
    booking_advice: Optional[str] = Field(default=None, description="Booking advice")

class RestaurantSearchResponse(BaseModel):
    """Restaurant search response"""
    query_used: str = Field(description="Search query used")
    total_results_found: int = Field(description="Total number of results found")
    restaurants: List[Restaurant] = Field(description="List of restaurants")
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata")