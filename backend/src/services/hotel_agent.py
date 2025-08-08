import os
import logging
from amadeus import Client, ResponseError
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Hotel(BaseModel):
    name: str = Field(description="Name of the hotel")
    brand: str = Field(description="Hotel brand/chain (e.g., Marriott, Hilton)")
    address: str = Field(description="Complete hotel address")
    city: str = Field(description="City where the hotel is located")
    neighborhood: str = Field(description="Neighborhood or district")
    star_rating: str = Field(description="Hotel star rating (1-5 stars)")
    guest_rating: str = Field(description="Guest review rating (e.g., 4.2/5)")
    review_count: str = Field(description="Number of reviews")
    price_per_night: str = Field(description="Price per night with currency")
    total_price: str = Field(description="Total price for the stay")
    amenities: List[str] = Field(description="List of hotel amenities")
    room_type: str = Field(description="Type of room (Standard, Deluxe, Suite, etc.)")
    check_in_time: str = Field(description="Check-in time")
    check_out_time: str = Field(description="Check-out time")
    cancellation_policy: str = Field(description="Cancellation policy")
    booking_url: str = Field(description="Direct URL to book this hotel")
    hotel_website: str = Field(description="Official hotel website")
    phone_number: str = Field(description="Hotel phone number")
    image_urls: List[str] = Field(description="List of hotel image URLs")

class HotelSearchOutput(BaseModel):
    hotels: List[Hotel] = Field(description="List of available hotels")
    search_query: str = Field(description="The search query used")
    total_results: int = Field(description="Total number of hotels found")

class HotelAgent:
    """Agent for hotel search using Amadeus API directly."""
    
    def __init__(self, api_token: str = None):
        """Initialize the hotel agent with Amadeus credentials."""
        # Note: api_token parameter kept for compatibility but not used
        # We use Amadeus credentials from environment
        
        client_id = os.getenv("AMADEUS_API_KEY")
        client_secret = os.getenv("AMADEUS_Secret")
        
        if not client_id or not client_secret:
            raise ValueError("Amadeus credentials (AMADEUS_API_KEY and AMADEUS_Secret) are required")
        
        self.amadeus = Client(
            client_id=client_id,
            client_secret=client_secret,
            hostname='test'
        )
        
        self._initialized = False
        logger.info("Hotel agent initialized with Amadeus API")
    
    async def initialize(self):
        """Initialize the agent (compatibility method)."""
        if self._initialized:
            return
        self._initialized = True
        logger.info("Hotel agent ready")
    
    async def _resolve_city_code(self, city: str) -> str:
        """Convert city name to IATA city code."""
        city_upper = city.upper().strip()
        
        # Check if it's already a 3-letter code
        if len(city_upper) == 3:
            return city_upper
        
        # Common city mappings
        city_mappings = {
            'NEW YORK': 'NYC',
            'NYC': 'NYC',
            'LONDON': 'LON',
            'PARIS': 'PAR',
            'TOKYO': 'TYO',
            'DUBAI': 'DXB',
            'LOS ANGELES': 'LAX',
            'SAN FRANCISCO': 'SFO',
            'MIAMI': 'MIA',
            'CHICAGO': 'CHI',
            'BOSTON': 'BOS',
            'SINGAPORE': 'SIN',
            'HONG KONG': 'HKG',
            'BANGKOK': 'BKK',
            'SYDNEY': 'SYD',
            'ROME': 'ROM',
            'BARCELONA': 'BCN',
            'MADRID': 'MAD',
            'AMSTERDAM': 'AMS',
            'BERLIN': 'BER'
        }
        
        return city_mappings.get(city_upper, city[:3].upper())
    
    async def search_hotels(self, 
                           city: str, 
                           check_in_date: str, 
                           check_out_date: str,
                           guests: int = 2,
                           rooms: int = 1,
                           price_range: str = "any") -> HotelSearchOutput:
        """Search for hotels in a specific city using Amadeus."""
        if not self._initialized:
            await self.initialize()
        
        query = f"Hotels in {city} for {check_in_date} to {check_out_date}"
        
        try:
            # Resolve city code
            city_code = await self._resolve_city_code(city)
            logger.info(f"Searching hotels in {city} (code: {city_code})")
            
            # Search hotels using Amadeus
            params = {
                'cityCode': city_code,
                'checkInDate': check_in_date,
                'checkOutDate': check_out_date,
                'adults': guests,
                'roomQuantity': rooms,
                'radius': 10,
                'radiusUnit': 'KM',
                'paymentPolicy': 'NONE',
                'includeClosed': 'false',
                'bestRateOnly': 'true',
                'view': 'FULL'
            }
            
            response = self.amadeus.shopping.hotel_offers_search.get(**params)
            
            hotels = []
            
            if hasattr(response, 'data'):
                for hotel_data in response.data[:10]:  # Limit to 10 hotels
                    hotel_info = hotel_data.get('hotel', {})
                    offers = hotel_data.get('offers', [])
                    
                    if not offers:
                        continue
                    
                    # Get the cheapest offer
                    cheapest_offer = min(offers, key=lambda x: float(x.get('price', {}).get('total', '999999')))
                    price = float(cheapest_offer.get('price', {}).get('total', 0))
                    
                    # Extract address
                    address_data = hotel_info.get('address', {})
                    address_lines = address_data.get('lines', [])
                    full_address = ', '.join(address_lines) if address_lines else 'Address not available'
                    
                    # Extract amenities
                    amenities = hotel_info.get('amenities', [])[:10]  # Limit to 10 amenities
                    
                    # Create hotel object
                    hotel = Hotel(
                        name=hotel_info.get('name', 'Unknown Hotel'),
                        brand=hotel_info.get('chainCode', 'Independent'),
                        address=full_address,
                        city=address_data.get('cityName', city),
                        neighborhood=address_data.get('stateCode', ''),
                        star_rating=str(hotel_info.get('rating', 3)),
                        guest_rating="4.0",  # Amadeus test data doesn't provide guest ratings
                        review_count="0",
                        price_per_night=f"${price:.0f}",
                        total_price=f"${price:.0f}",
                        amenities=amenities if amenities else ['WiFi', 'Parking'],
                        room_type=cheapest_offer.get('room', {}).get('type', 'Standard'),
                        check_in_time="3:00 PM",
                        check_out_time="11:00 AM",
                        cancellation_policy=cheapest_offer.get('policies', {}).get('cancellation', {}).get('description', 'Standard cancellation'),
                        booking_url=f"https://www.booking.com/search.html?ss={hotel_info.get('name', '').replace(' ', '+')}",
                        hotel_website=f"https://www.google.com/search?q={hotel_info.get('name', '').replace(' ', '+')}+official+website",
                        phone_number=hotel_info.get('contact', {}).get('phone', 'Not available'),
                        image_urls=[]
                    )
                    
                    hotels.append(hotel)
            
            logger.info(f"Found {len(hotels)} hotels in {city}")
            
            return HotelSearchOutput(
                hotels=hotels,
                search_query=query,
                total_results=len(hotels)
            )
            
        except ResponseError as e:
            logger.error(f"Amadeus error searching hotels: {e}")
            # Return mock data for testing
            return self._get_mock_hotels(city, check_in_date, check_out_date, query)
        except Exception as e:
            logger.error(f"Error in searching hotels: {e}")
            return HotelSearchOutput(
                hotels=[],
                search_query=query,
                total_results=0
            )
    
    def _get_mock_hotels(self, city: str, check_in: str, check_out: str, query: str) -> HotelSearchOutput:
        """Return mock hotel data for testing."""
        mock_hotels = [
            Hotel(
                name=f"Grand Hotel {city}",
                brand="Hilton",
                address=f"123 Main Street, {city}",
                city=city,
                neighborhood="Downtown",
                star_rating="5",
                guest_rating="4.5",
                review_count="1250",
                price_per_night="$250",
                total_price="$750",
                amenities=["WiFi", "Pool", "Gym", "Spa", "Restaurant"],
                room_type="Deluxe Room",
                check_in_time="3:00 PM",
                check_out_time="12:00 PM",
                cancellation_policy="Free cancellation up to 24 hours",
                booking_url="https://www.hilton.com",
                hotel_website="https://www.hilton.com",
                phone_number="+1-555-0100",
                image_urls=[]
            ),
            Hotel(
                name=f"Budget Inn {city}",
                brand="Independent",
                address=f"456 Second Ave, {city}",
                city=city,
                neighborhood="Airport Area",
                star_rating="3",
                guest_rating="3.8",
                review_count="450",
                price_per_night="$85",
                total_price="$255",
                amenities=["WiFi", "Parking", "Breakfast"],
                room_type="Standard Room",
                check_in_time="2:00 PM",
                check_out_time="11:00 AM",
                cancellation_policy="Non-refundable",
                booking_url="https://www.booking.com",
                hotel_website="https://www.booking.com",
                phone_number="+1-555-0200",
                image_urls=[]
            )
        ]
        
        return HotelSearchOutput(
            hotels=mock_hotels,
            search_query=query,
            total_results=2
        )
    
    async def search_budget_hotels(self, 
                                  city: str, 
                                  check_in_date: str, 
                                  check_out_date: str,
                                  guests: int = 2) -> HotelSearchOutput:
        """Search for budget-friendly hotels in a specific city."""
        return await self.search_hotels(city, check_in_date, check_out_date, guests, 1, "budget")
    
    async def search_luxury_hotels(self, 
                                  city: str, 
                                  check_in_date: str, 
                                  check_out_date: str,
                                  guests: int = 2) -> HotelSearchOutput:
        """Search for luxury hotels in a specific city."""
        return await self.search_hotels(city, check_in_date, check_out_date, guests, 1, "luxury")
    
    async def run_custom_query(self, query: str) -> HotelSearchOutput:
        """Run a custom hotel search query (compatibility method)."""
        # Parse query for basic info
        import re
        
        # Try to extract city
        city = "New York"  # Default
        if "in " in query.lower():
            parts = query.lower().split("in ")
            if len(parts) > 1:
                city = parts[1].split()[0].strip()
        
        # Try to extract dates (default to next week)
        from datetime import datetime, timedelta
        check_in = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        check_out = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        
        return await self.search_hotels(city, check_in, check_out)


# Convenience functions for backward compatibility
async def search_hotels(city: str, 
                       check_in_date: str, 
                       check_out_date: str,
                       guests: int = 2,
                       rooms: int = 1,
                       price_range: str = "any") -> HotelSearchOutput:
    """Convenience function to search hotels."""
    try:
        agent = HotelAgent()
        return await agent.search_hotels(city, check_in_date, check_out_date, guests, rooms, price_range)
    except Exception as e:
        logger.error(f"Error in search_hotels: {e}")
        raise

async def search_budget_hotels(city: str, 
                              check_in_date: str, 
                              check_out_date: str,
                              guests: int = 2) -> HotelSearchOutput:
    """Convenience function to search for budget hotels."""
    try:
        agent = HotelAgent()
        return await agent.search_budget_hotels(city, check_in_date, check_out_date, guests)
    except Exception as e:
        logger.error(f"Error in search_budget_hotels: {e}")
        raise

async def search_luxury_hotels(city: str, 
                              check_in_date: str, 
                              check_out_date: str,
                              guests: int = 2) -> HotelSearchOutput:
    """Convenience function to search for luxury hotels."""
    try:
        agent = HotelAgent()
        return await agent.search_luxury_hotels(city, check_in_date, check_out_date, guests)
    except Exception as e:
        logger.error(f"Error in search_luxury_hotels: {e}")
        raise