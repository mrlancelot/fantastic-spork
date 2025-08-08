"""User Service - Clean user management and Convex integration

Handles:
- User authentication and storage (via Convex)
- Trip data management
- User preferences and settings
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..core.config import get_settings
from ..models.requests import StoreUserRequest

try:
    from convex import ConvexClient
except ImportError:
    ConvexClient = None

class UserService:
    """Clean user service for Convex integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self._convex_client = None
    
    @property
    def convex_client(self) -> Optional[ConvexClient]:
        """Get Convex client instance (lazy initialization)"""
        if self._convex_client is None and ConvexClient and self.settings.convex_url:
            try:
                self._convex_client = ConvexClient(self.settings.convex_url)
            except Exception as e:
                print(f"Failed to initialize Convex client: {e}")
        return self._convex_client
    
    async def store_user(self, request: StoreUserRequest) -> Dict[str, Any]:
        """Store user data from Clerk authentication"""
        try:
            if self.convex_client:
                # Try to store in Convex
                user_data = {
                    "clerk_id": request.clerk_user_id,
                    "email": request.email,
                    "full_name": request.name or "",
                    "image_url": request.image_url or "",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                result = self.convex_client.mutation(
                    "users:storeFromBackend",
                    user_data
                )
                
                return {
                    "success": True,
                    "user_id": result,
                    "message": "User stored successfully in Convex"
                }
            else:
                # Fallback for development/demo
                return {
                    "success": True,
                    "user_id": f"user_{request.clerk_user_id}",
                    "message": "User stored successfully (demo mode)",
                    "demo_mode": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store user data"
            }
    
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Clerk ID"""
        try:
            if self.convex_client:
                result = self.convex_client.query(
                    "users:getByClerkId",
                    {"clerk_id": clerk_id}
                )
                return result
            else:
                # Return mock user for development
                return {
                    "clerk_id": clerk_id,
                    "email": "demo@example.com",
                    "full_name": "Demo User",
                    "demo_mode": True
                }
        except Exception as e:
            print(f"Failed to get user by Clerk ID: {e}")
            return None
    
    async def save_trip_itinerary(self, itinerary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save trip itinerary to Convex"""
        try:
            if self.convex_client:
                result = self.convex_client.mutation(
                    "trips:createFromBackend",
                    itinerary_data
                )
                
                return {
                    "success": True,
                    "trip_id": result,
                    "message": "Itinerary saved successfully"
                }
            else:
                # Fallback for demo mode
                import uuid
                return {
                    "success": True,
                    "trip_id": str(uuid.uuid4()),
                    "message": "Itinerary saved (demo mode)",
                    "demo_mode": True
                }
                
        except Exception as e:
            raise Exception(f"Failed to save itinerary: {str(e)}")
    
    async def get_user_trips(self, clerk_id: str) -> List[Dict[str, Any]]:
        """Get all trips for a user"""
        try:
            if self.convex_client:
                result = self.convex_client.query(
                    "trips:getUserTrips",
                    {"clerk_id": clerk_id}
                )
                return result or []
            else:
                # Return mock trips for development
                return [
                    {
                        "id": "trip_1",
                        "destination": "Paris",
                        "start_date": "2024-09-15",
                        "end_date": "2024-09-22",
                        "status": "planned",
                        "demo_mode": True
                    }
                ]
        except Exception as e:
            print(f"Failed to get user trips: {e}")
            return []
    
    async def update_user_preferences(self, clerk_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            if self.convex_client:
                result = self.convex_client.mutation(
                    "users:updatePreferences",
                    {
                        "clerk_id": clerk_id,
                        "preferences": preferences
                    }
                )
                
                return {
                    "success": True,
                    "message": "Preferences updated successfully"
                }
            else:
                return {
                    "success": True,
                    "message": "Preferences updated (demo mode)",
                    "demo_mode": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update preferences"
            }
