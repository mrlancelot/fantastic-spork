"""
Booking.com Hotel Scraper
Reliable scraper for finding hotels on Booking.com
"""

import asyncio
import re
import json
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Data Models ====================

@dataclass
class SearchParams:
    """Hotel search parameters"""
    destination: str
    check_in: str  # Format: "YYYY-MM-DD" or "Aug 10, 2025"
    check_out: str
    adults: int = 2
    children: int = 0
    rooms: int = 1

@dataclass
class HotelResult:
    """Hotel result structure"""
    name: str
    price: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    location: Optional[str] = None
    amenities: List[str] = field(default_factory=list)
    source: str = "Booking.com"
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

# ==================== Booking.com Scraper ====================

class BookingComScraper:
    """Scraper for Booking.com hotels"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def initialize(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        print(f"🏨 Launching hotel scraper browser (headless={self.headless})...")
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await context.new_page()
        self.page.set_default_timeout(30000)
        
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
    
    async def search_hotels(self, params: SearchParams) -> List[HotelResult]:
        """Search hotels on Booking.com"""
        logger.info(f"🏨 Searching Booking.com for {params.destination}")
        logger.info(f"📅 Dates: {params.check_in} to {params.check_out}")
        
        results = []
        try:
            # Format dates for Booking.com (YYYY-MM-DD)
            check_in = self._format_date(params.check_in)
            check_out = self._format_date(params.check_out)
            
            # Build URL with search parameters
            url = (
                f"https://www.booking.com/searchresults.html"
                f"?ss={params.destination}"
                f"&checkin={check_in}"
                f"&checkout={check_out}"
                f"&group_adults={params.adults}"
                f"&group_children={params.children}"
                f"&no_rooms={params.rooms}"
            )
            
            logger.info(f"🔗 URL: {url}")
            
            await self.page.goto(url)
            await self.page.wait_for_timeout(3000)
            
            # Scroll to load more results
            for _ in range(5):
                await self.page.evaluate('window.scrollBy(0, 1000)')
                await self.page.wait_for_timeout(500)
            
            # Extract hotel data
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Booking.com hotel card selectors
            hotel_selectors = [
                '[data-testid="property-card"]',
                '.sr_property_block',
                '[data-hotelid]'
            ]
            
            for selector in hotel_selectors:
                elements = soup.select(selector)
                for elem in elements[:30]:
                    hotel = self._parse_hotel(elem)
                    if hotel:
                        results.append(hotel)
            
            logger.info(f"✅ Found {len(results)} hotels on Booking.com")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        return results
    
    def _parse_hotel(self, element) -> Optional[HotelResult]:
        """Parse hotel element"""
        try:
            hotel = HotelResult(name="")
            
            # Extract name
            name_selectors = [
                '[data-testid="title"]',
                '.sr-hotel__name',
                'h3'
            ]
            for sel in name_selectors:
                name_elem = element.select_one(sel)
                if name_elem:
                    hotel.name = name_elem.get_text(strip=True)
                    break
            
            if not hotel.name:
                return None
            
            # Extract price
            price_selectors = [
                '[data-testid="price-and-discounted-price"]',
                '.bui-price-display__value',
                '[class*="price"]'
            ]
            for sel in price_selectors:
                price_elem = element.select_one(sel)
                if price_elem:
                    hotel.price = price_elem.get_text(strip=True)
                    break
            
            # Extract rating
            rating_selectors = [
                '[data-testid="review-score"]',
                '.bui-review-score__badge'
            ]
            for sel in rating_selectors:
                rating_elem = element.select_one(sel)
                if rating_elem:
                    try:
                        rating_text = rating_elem.get_text(strip=True)
                        # Extract numeric rating
                        match = re.search(r'[\d.]+', rating_text)
                        if match:
                            hotel.rating = float(match.group())
                    except:
                        pass
                    break
            
            # Extract review count
            review_elem = element.select_one('[class*="review"]')
            if review_elem:
                text = review_elem.get_text()
                match = re.search(r'([\d,]+)\s*reviews?', text, re.IGNORECASE)
                if match:
                    try:
                        hotel.reviews_count = int(match.group(1).replace(',', ''))
                    except:
                        pass
            
            # Extract location
            location_elem = element.select_one('[data-testid="address"], [class*="location"]')
            if location_elem:
                hotel.location = location_elem.get_text(strip=True)
            
            return hotel
            
        except Exception:
            return None
    
    def _format_date(self, date_str: str) -> str:
        """Format date for URL (YYYY-MM-DD format)"""
        if '-' in date_str and len(date_str) == 10:
            return date_str
        
        # Convert from "Aug 10, 2025" to "2025-08-10"
        months = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'June': '06', 'July': '07', 'August': '08', 'September': '09',
            'October': '10', 'November': '11', 'December': '12'
        }
        
        try:
            # Handle "Aug 10, 2025" format
            parts = date_str.replace(',', '').split()
            if len(parts) == 3:
                month = months.get(parts[0], '08')
                day = parts[1].zfill(2)
                year = parts[2]
                return f"{year}-{month}-{day}"
        except:
            pass
        
        # Default fallback
        return "2025-08-10"

# ==================== Main Test Function ====================

async def test_booking_scraper():
    """Test the Booking.com scraper"""
    
    # Test parameters
    params = SearchParams(
        destination="Knoxville, Tennessee",
        check_in="2025-08-16",
        check_out="2025-08-19",
        adults=2,
        rooms=1
    )
    
    scraper = BookingComScraper(headless=False)
    
    try:
        await scraper.initialize()
        hotels = await scraper.search_hotels(params)
        
        print(f"\n✅ Found {len(hotels)} hotels")
        
        # Display top 5 hotels
        for i, hotel in enumerate(hotels[:5], 1):
            print(f"\n{i}. {hotel.name}")
            if hotel.price:
                print(f"   💰 Price: {hotel.price}")
            if hotel.rating:
                print(f"   ⭐ Rating: {hotel.rating}/10")
            if hotel.reviews_count:
                print(f"   📝 Reviews: {hotel.reviews_count:,}")
            if hotel.location:
                print(f"   📍 Location: {hotel.location}")
        
        # Save results
        results_dict = [asdict(hotel) for hotel in hotels]
        with open('booking_results.json', 'w') as f:
            json.dump(results_dict, f, indent=2)
        print(f"\n💾 Results saved to booking_results.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_booking_scraper())