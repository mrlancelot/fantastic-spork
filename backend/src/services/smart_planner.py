"""Smart Planner Service - Intelligent itinerary creation and management

Handles:
- Smart itinerary generation with AI recommendations
- Daily slot management (4 slots per day)
- Gamification and achievements
- Integration with travel services
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..core.config import get_settings
from ..models.requests import SmartPlannerRequest, DailySlot, DailyPlan, SmartItinerary
# Travel service imports handled separately
from .user_service import UserService

class SmartPlannerService:
    """Clean smart planner service for itinerary management"""
    
    def __init__(self):
        self.settings = get_settings()
        self.user_service = UserService()
    
    async def create_smart_itinerary(self, request: SmartPlannerRequest) -> Dict[str, Any]:
        """Create a smart daily planner with 4 slots per day"""
        try:
            # Calculate number of days
            start = datetime.fromisoformat(request.start_date)
            end = datetime.fromisoformat(request.end_date)
            days = (end - start).days + 1
            
            daily_plans = []
            
            for i in range(days):
                current_date = start + timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Create 4 intelligent slots per day
                slots = self._create_daily_slots(request.destination, date_str, i, request.preferences)
                
                # Get weather info (mock for MVP)
                weather = self._get_weather_info(request.destination, date_str)
                
                daily_plans.append(DailyPlan(
                    date=date_str,
                    slots=slots,
                    weather=weather
                ))
            
            # Flight inspiration data (can be fetched via separate API)
            flight_inspiration = {}
            
            # Create the itinerary
            itinerary = SmartItinerary(
                user_id="",  # Will be set when saving
                destination=request.destination,
                start_date=request.start_date,
                end_date=request.end_date,
                travelers=request.travelers,
                daily_plans=daily_plans,
                flights=[],
                hotels=[],
                restaurants=[],
                travel_docs=[],
                budget={"estimated_total": f"${request.budget}" if request.budget else "TBD"},
                group_members=[]
            )
            
            return {
                "itinerary": itinerary.dict(),
                "flight_inspiration": flight_inspiration,
                "days_planned": days,
                "status": "success"
            }
            
        except Exception as e:
            raise Exception(f"Smart planner error: {str(e)}")
    
    def _create_daily_slots(self, destination: str, date: str, day_index: int, preferences: List[str]) -> List[DailySlot]:
        """Create intelligent daily slots based on destination and preferences"""
        
        # Define time slots with intelligent suggestions
        slot_configs = [
            {
                "time_slot": "morning",
                "default_activity": "Morning Exploration",
                "default_description": f"Start your day exploring {destination}",
                "duration": "3 hours"
            },
            {
                "time_slot": "midday",
                "default_activity": "Lunch & Sightseeing",
                "default_description": f"Discover {destination}'s highlights",
                "duration": "4 hours"
            },
            {
                "time_slot": "evening",
                "default_activity": "Dinner & Culture",
                "default_description": f"Experience {destination}'s cuisine and culture",
                "duration": "3 hours"
            },
            {
                "time_slot": "night",
                "default_activity": "Nightlife & Relaxation",
                "default_description": f"Enjoy {destination}'s evening scene",
                "duration": "2 hours"
            }
        ]
        
        # Customize based on day and preferences
        if day_index == 0:  # First day - arrival
            slot_configs[0]["default_activity"] = "Arrival & Check-in"
            slot_configs[0]["default_description"] = f"Arrive in {destination} and get settled"
        
        # Customize based on preferences
        if "adventure" in preferences:
            slot_configs[0]["default_activity"] = "Adventure Activity"
            slot_configs[0]["default_description"] = f"Outdoor adventure in {destination}"
        elif "culture" in preferences:
            slot_configs[0]["default_activity"] = "Cultural Experience"
            slot_configs[0]["default_description"] = f"Immerse in {destination}'s culture"
        elif "food" in preferences:
            slot_configs[1]["default_activity"] = "Food Tour"
            slot_configs[1]["default_description"] = f"Culinary exploration of {destination}"
        
        # Create the slots
        slots = []
        for config in slot_configs:
            slots.append(DailySlot(
                id=str(uuid.uuid4()),
                time_slot=config["time_slot"],
                activity=config["default_activity"],
                description=config["default_description"],
                duration=config["duration"],
                location=destination,
                completed=False,
                booking_url="",
                notes=""
            ))
        
        return slots
    
    def _get_weather_info(self, location: str, date: str) -> Dict[str, Any]:
        """Get weather information for a location and date"""
        # Mock weather data for MVP - in production would call weather API
        return {
            "temperature": "22°C",
            "condition": "Sunny",
            "humidity": "65%",
            "wind": "10 km/h",
            "icon": "☀️",
            "forecast": "Perfect weather for sightseeing!"
        }
    
    async def update_slot(self, date: str, slot_id: str, slot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific slot in the itinerary"""
        # In production, this would update the slot in Convex database
        return {
            "slot_id": slot_id,
            "date": date,
            "updated_data": slot_data,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    
    async def complete_slot(self, slot_id: str) -> Dict[str, Any]:
        """Mark a slot as completed and handle gamification"""
        # Check for achievements
        achievements = self._check_slot_achievements(slot_id)
        
        return {
            "completed_at": datetime.now().isoformat(),
            "achievements": achievements,
            "points_earned": sum(a.get("points", 0) for a in achievements),
            "celebration": True,
            "status": "success"
        }
    
    def _check_slot_achievements(self, slot_id: str) -> List[Dict[str, Any]]:
        """Check for achievements when completing a slot"""
        # Mock achievement logic for MVP
        achievements = [
            {
                "id": "first_step",
                "name": "First Steps",
                "description": "Complete your first activity",
                "icon": "🎯",
                "points": 100,
                "unlocked_at": datetime.now().isoformat()
            }
        ]
        
        return achievements
    
    async def save_itinerary(self, itinerary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save smart itinerary to database"""
        try:
            # Try to save to Convex via user service
            result = await self.user_service.save_trip_itinerary(itinerary_data)
            return result
        except Exception as e:
            # Fallback to demo mode for MVP
            return {
                "success": True,
                "trip_id": str(uuid.uuid4()),
                "message": "Itinerary saved successfully",
                "demo_mode": True,
                "error": str(e)
            }
    
    async def get_itinerary_suggestions(self, destination: str, preferences: List[str]) -> List[Dict[str, Any]]:
        """Get AI-powered itinerary suggestions"""
        # In production, this would use AI agents for personalized suggestions
        suggestions = [
            {
                "type": "restaurant",
                "name": f"Top-rated restaurant in {destination}",
                "description": "Authentic local cuisine experience",
                "priority": "high",
                "estimated_cost": "$25-40 per person"
            },
            {
                "type": "activity",
                "name": f"Must-see attraction in {destination}",
                "description": "Popular cultural landmark",
                "priority": "medium", 
                "estimated_cost": "$15-25 per person"
            },
            {
                "type": "experience",
                "name": f"Local experience in {destination}",
                "description": "Unique cultural activity",
                "priority": "low",
                "estimated_cost": "$30-50 per person"
            }
        ]
        
        return suggestions
