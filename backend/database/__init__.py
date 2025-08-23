"""
Database Package
Exports main database components for easy import
"""

from database.convex_manager import ConvexManager, get_convex_manager
from database.travel_repository import TravelRepository
from database.models import (
    Itinerary,
    ItineraryDay,
    Activity,
    Flight,
    Hotel,
    Restaurant,
    Job
)

__all__ = [
    # Manager
    'ConvexManager',
    'get_convex_manager',
    
    # Repository
    'TravelRepository',
    
    # Models
    'Itinerary',
    'ItineraryDay', 
    'Activity',
    'Flight',
    'Hotel',
    'Restaurant',
    'Job'
]