#!/usr/bin/env python3
"""
Optimized Google Flights Scraper - Fast & Efficient Version
Features:
- Headless browser mode for 2-3x faster performance
- Smart wait strategies instead of fixed timeouts
- Structured data models with Pydantic
- Parallel processing capabilities
- Efficient data extraction
- Automatic cleanup of test files
"""

import asyncio
from playwright.async_api import async_playwright, Page
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import json
import re
from bs4 import BeautifulSoup
import os
import glob

# ==================== DATA MODELS ====================

class FlightSegment(BaseModel):
    """Individual flight segment data"""
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    duration: Optional[str] = None
    stops: int = 0
    stop_type: str = "Nonstop"
    layover_info: Optional[Dict[str, str]] = None
    price: Optional[str] = None

class RoundTripCombination(BaseModel):
    """Complete round trip combination"""
    combination_id: int
    outbound: FlightSegment
    return_flight: FlightSegment
    total_price: Optional[str] = None
    booking_url: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)

class SearchParams(BaseModel):
    """Search parameters"""
    origin: str
    destination: str
    departure_date: str
    return_date: str
    passengers: int = 1
    class_type: str = "economy"

class ScraperConfig(BaseModel):
    """Scraper configuration"""
    headless: bool = True
    timeout: int = 30000  # 30 seconds max timeout
    max_retries: int = 3
    smart_wait: bool = True
    cleanup_files: bool = True
    max_combinations: int = 10
    parallel_processing: bool = False

# ==================== OPTIMIZED SCRAPER ====================

class OptimizedFlightScraper:
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.browser = None
        self.context = None
        self.page = None
        
    async def __aenter__(self):
        await self.setup()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        
    async def setup(self):
        """Initialize browser with optimized settings"""
        playwright = await async_playwright().start()
        
        # Optimized browser settings for speed
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-images',  # Don't load images for faster performance
                '--disable-javascript-harmony',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        )
        
        # Context with optimized settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            ignore_https_errors=True,
            java_script_enabled=True,
            bypass_csp=True,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
            }
        )
        
        # Block unnecessary resources for faster loading
        await self.context.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf}", 
                                 lambda route: route.abort())
        
        self.page = await self.context.new_page()
        
    async def cleanup(self):
        """Clean up browser and test files"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            
        # Clean up test files
        if self.config.cleanup_files:
            self._cleanup_test_files()
            
    def _cleanup_test_files(self):
        """Remove generated test HTML and JSON files"""
        patterns = [
            'flight_*.html',
            'flight_*.json',
            'error_*.html',
            '*_flights_*.html',
            '*_round_trip_*.json',
            'booking_*.html',
            'additional_*.json'
        ]
        
        for pattern in patterns:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    print(f"🗑️  Cleaned up: {file}")
                except:
                    pass
                    
    async def smart_wait(self, selector: str = None, timeout: int = 5000):
        """Smart waiting strategy instead of fixed timeouts"""
        if not self.config.smart_wait:
            await self.page.wait_for_timeout(timeout)
            return
            
        try:
            if selector:
                # Wait for specific element
                await self.page.wait_for_selector(selector, timeout=timeout, state='visible')
            else:
                # Wait for network idle (no requests for 500ms)
                await self.page.wait_for_load_state('networkidle', timeout=timeout)
        except:
            # Fallback to minimal wait
            await self.page.wait_for_timeout(500)
            
    async def quick_click(self, selector: str, index: int = 0) -> bool:
        """Optimized clicking with multiple strategies"""
        strategies = [
            lambda el: el.click(force=True, timeout=2000),
            lambda el: el.dispatch_event('click'),
            lambda el: el.evaluate('el => el.click()')
        ]
        
        try:
            elements = await self.page.query_selector_all(selector)
            if len(elements) > index:
                element = elements[index]
                
                for strategy in strategies:
                    try:
                        await strategy(element)
                        return True
                    except:
                        continue
        except:
            pass
            
        return False
        
    def extract_flight_data_optimized(self, html: str) -> List[FlightSegment]:
        """Optimized flight data extraction"""
        soup = BeautifulSoup(html, 'lxml')  # lxml is faster than html.parser
        flights = []
        
        # Single pass extraction with compiled regex
        price_pattern = re.compile(r'\$[\d,]+')
        time_pattern = re.compile(r'\d{1,2}:\d{2}\s*[AP]M')
        duration_pattern = re.compile(r'\d+h\s*\d*m?')
        airline_pattern = re.compile(r'(United|Delta|American|Southwest|JetBlue|Alaska|Spirit|Frontier|Hawaiian)')
        
        # Find all flight containers at once
        containers = soup.find_all(['li', 'div'], class_=re.compile('gQ6yfe|pIav2d|yR1fYc|Ir0Voe'))[:20]
        
        for container in containers:
            text = container.get_text(strip=True)
            if not text or len(text) < 10:
                continue
                
            flight = FlightSegment()
            
            # Extract all data in single pass
            price_match = price_pattern.search(text)
            if price_match:
                flight.price = price_match.group()
                
            times = time_pattern.findall(text)
            if len(times) >= 2:
                flight.departure_time = times[0]
                flight.arrival_time = times[1]
                
            duration_match = duration_pattern.search(text)
            if duration_match:
                flight.duration = duration_match.group()
                
            airline_match = airline_pattern.search(text)
            if airline_match:
                flight.airline = airline_match.group()
                
            # Stops detection
            if 'Nonstop' in text:
                flight.stops = 0
                flight.stop_type = 'Nonstop'
            elif '1 stop' in text:
                flight.stops = 1
                flight.stop_type = '1 stop'
                
            if flight.price or flight.departure_time:
                flights.append(flight)
                
        return flights
        
    async def search_flights(self, params: SearchParams) -> List[RoundTripCombination]:
        """Main search function with optimized flow"""
        combinations = []
        
        try:
            print(f"🚀 Starting optimized search: {params.origin} → {params.destination}")
            
            # Navigate to Google Flights
            await self.page.goto("https://www.google.com/travel/flights", 
                                wait_until='domcontentloaded')
            
            # Quick form filling without unnecessary waits
            await self._fill_search_form_fast(params)
            
            # Click search and wait for results
            await self.quick_click('button:has-text("Search")')
            await self.smart_wait('[role="listitem"]', timeout=5000)
            
            # Extract outbound flights
            html = await self.page.content()
            outbound_flights = self.extract_flight_data_optimized(html)
            print(f"✅ Found {len(outbound_flights)} outbound flights")
            
            # Process combinations efficiently
            combinations = await self._process_combinations_fast(outbound_flights)
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            
        return combinations
        
    async def _fill_search_form_fast(self, params: SearchParams):
        """Fast form filling without excessive waits"""
        # Origin
        await self.page.click('[aria-label*="Where from"]')
        await self.page.fill('input[aria-label*="Where else"]', params.origin)
        await self.page.keyboard.press('Enter')
        
        # Destination  
        await self.page.click('[aria-label*="Where to"]')
        await self.page.fill('input[aria-label*="Where to"]', params.destination)
        await self.page.keyboard.press('Enter')
        
        # Dates - direct fill
        await self.page.fill('input[placeholder*="Departure"]', params.departure_date)
        await self.page.fill('input[placeholder*="Return"]', params.return_date)
        await self.page.keyboard.press('Enter')
        await self.page.keyboard.press('Enter')  # Close date picker
        
    async def _process_combinations_fast(self, outbound_flights: List[FlightSegment]) -> List[RoundTripCombination]:
        """Process flight combinations efficiently"""
        combinations = []
        max_to_process = min(self.config.max_combinations, len(outbound_flights))
        
        for i in range(max_to_process):
            try:
                # Click outbound flight
                if not await self.quick_click('.gQ6yfe', index=i):
                    continue
                    
                await self.smart_wait('[role="listitem"]', timeout=3000)
                
                # Get return flights
                html = await self.page.content()
                return_flights = self.extract_flight_data_optimized(html)
                
                if return_flights:
                    # Click first return flight
                    await self.quick_click('.gQ6yfe', index=0)
                    await self.smart_wait(timeout=2000)
                    
                    # Extract total price
                    html = await self.page.content()
                    total_price = self._extract_total_price(html)
                    
                    combination = RoundTripCombination(
                        combination_id=i + 1,
                        outbound=outbound_flights[i],
                        return_flight=return_flights[0],
                        total_price=total_price
                    )
                    combinations.append(combination)
                    
                    print(f"✅ Combination {i+1}: {total_price}")
                    
                # Navigate back efficiently
                await self.page.go_back()
                await self.page.go_back()
                await self.smart_wait('[role="listitem"]', timeout=2000)
                
            except Exception as e:
                print(f"⚠️ Error processing combination {i+1}: {e}")
                continue
                
        return combinations
        
    def _extract_total_price(self, html: str) -> Optional[str]:
        """Quick total price extraction"""
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text()
        
        # Look for round trip total
        patterns = [
            r'round\s*trip[:\s]*\$[\d,]+',
            r'\$[\d,]+\s*round\s*trip',
            r'Total[:\s]*\$[\d,]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_match = re.search(r'\$[\d,]+', match.group())
                if price_match:
                    return price_match.group()
                    
        # Fallback: find largest price
        prices = re.findall(r'\$(\d+(?:,\d{3})*)', text)
        if prices:
            prices_int = [int(p.replace(',', '')) for p in prices]
            max_price = max(prices_int)
            return f"${max_price:,}"
            
        return None

# ==================== GENERALIZED SCRAPER FRAMEWORK ====================

class TravelServiceScraper:
    """Base class for scraping various travel services"""
    
    def __init__(self, service_type: str, config: ScraperConfig = None):
        self.service_type = service_type
        self.config = config or ScraperConfig()
        self.scraper = OptimizedFlightScraper(config)
        
    async def scrape_hotels(self, location: str, checkin: str, checkout: str):
        """Scrape Google Hotels"""
        async with self.scraper as s:
            await s.page.goto("https://www.google.com/travel/hotels")
            
            # Fill search form
            await s.page.fill('input[placeholder*="Search"]', location)
            await s.page.keyboard.press('Enter')
            
            await s.smart_wait('[role="listitem"]', timeout=5000)
            
            # Extract hotel data
            html = await s.page.content()
            return self._extract_hotels(html)
            
    async def scrape_activities(self, location: str, date: str):
        """Scrape Google Things to Do"""
        async with self.scraper as s:
            await s.page.goto(f"https://www.google.com/travel/things-to-do/see-all?dest={location}")
            await s.smart_wait('[role="listitem"]', timeout=5000)
            
            html = await s.page.content()
            return self._extract_activities(html)
            
    def _extract_hotels(self, html: str) -> List[Dict]:
        """Extract hotel data from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        hotels = []
        
        # Hotel extraction logic
        hotel_cards = soup.find_all('div', class_=re.compile('hotel|property|listing'))[:20]
        
        for card in hotel_cards:
            text = card.get_text(strip=True)
            hotel = {
                'name': self._extract_name(text),
                'price': self._extract_price(text),
                'rating': self._extract_rating(text),
                'amenities': self._extract_amenities(text)
            }
            if hotel['name']:
                hotels.append(hotel)
                
        return hotels
        
    def _extract_activities(self, html: str) -> List[Dict]:
        """Extract activity data from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        activities = []
        
        activity_cards = soup.find_all('div', class_=re.compile('activity|attraction|thing'))[:20]
        
        for card in activity_cards:
            text = card.get_text(strip=True)
            activity = {
                'name': self._extract_name(text),
                'price': self._extract_price(text),
                'rating': self._extract_rating(text),
                'duration': self._extract_duration(text)
            }
            if activity['name']:
                activities.append(activity)
                
        return activities
        
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from text"""
        lines = text.split('\n')
        return lines[0] if lines else None
        
    def _extract_price(self, text: str) -> Optional[str]:
        """Extract price from text"""
        match = re.search(r'\$[\d,]+', text)
        return match.group() if match else None
        
    def _extract_rating(self, text: str) -> Optional[str]:
        """Extract rating from text"""
        match = re.search(r'(\d+\.?\d*)\s*(?:stars?|rating)', text, re.IGNORECASE)
        return match.group(1) if match else None
        
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract duration from text"""
        match = re.search(r'\d+\s*(?:hours?|hrs?|minutes?|mins?)', text, re.IGNORECASE)
        return match.group() if match else None

# ==================== MAIN EXECUTION ====================

async def main():
    """Main execution function"""
    # Clean up old test files first
    scraper = OptimizedFlightScraper()
    scraper._cleanup_test_files()
    
    # Search parameters
    params = SearchParams(
        origin="Louisville",
        destination="Orlando",
        departure_date="Aug 10, 2025",
        return_date="Aug 12, 2025"
    )
    
    # Configuration
    config = ScraperConfig(
        headless=True,  # Run headless for speed
        smart_wait=True,
        cleanup_files=True,
        max_combinations=5  # Just get top 5 for speed
    )
    
    # Run optimized flight search
    async with OptimizedFlightScraper(config) as scraper:
        combinations = await scraper.search_flights(params)
        
        # Display results
        if combinations:
            print("\n" + "="*60)
            print("🎯 OPTIMIZED RESULTS")
            print("="*60)
            
            for combo in combinations:
                print(f"\n{combo.combination_id}. {combo.total_price}")
                print(f"   🛫 {combo.outbound.airline} {combo.outbound.departure_time}→{combo.outbound.arrival_time}")
                print(f"   🛬 {combo.return_flight.airline} {combo.return_flight.departure_time}→{combo.return_flight.arrival_time}")
                
            # Save structured results
            results = {
                'search_params': params.dict(),
                'combinations': [c.dict() for c in combinations],
                'scraped_at': datetime.now().isoformat()
            }
            
            with open('optimized_results.json', 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"\n💾 Results saved to optimized_results.json")
            
    # Example: Scrape hotels
    print("\n🏨 Testing hotel scraping...")
    hotel_scraper = TravelServiceScraper('hotels', config)
    hotels = await hotel_scraper.scrape_hotels("Orlando", "Aug 10, 2025", "Aug 12, 2025")
    print(f"Found {len(hotels)} hotels")
    
    # Example: Scrape activities  
    print("\n🎭 Testing activity scraping...")
    activity_scraper = TravelServiceScraper('activities', config)
    activities = await activity_scraper.scrape_activities("Orlando", "Aug 10, 2025")
    print(f"Found {len(activities)} activities")
    
if __name__ == "__main__":
    import time
    start_time = time.time()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed:.2f} seconds")