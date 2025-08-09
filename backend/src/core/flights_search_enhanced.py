#!/usr/bin/env python3
"""
Enhanced Google Flights Scraper - Production Ready
Maintains all functionality from flights_search.py but optimized for speed and reliability
"""

import asyncio
from playwright.async_api import async_playwright, Page
from datetime import datetime
import time
import json
from bs4 import BeautifulSoup
import re
import os
import glob
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ==================== Configuration ====================

@dataclass
class ScraperConfig:
    """Configuration for the scraper"""
    headless: bool = False  # Set to True for production
    slow_mo: int = 100  # Reduced from 300
    timeout: int = 30000
    wait_short: int = 500  # Reduced from 1000-2000
    wait_medium: int = 1500  # Reduced from 3000
    wait_long: int = 3000  # Reduced from 5000
    max_flight_details: int = 5
    max_combinations: int = 3
    cleanup_files: bool = True
    save_html: bool = True  # For debugging
    save_json: bool = True

# ==================== Data Models ====================

@dataclass
class FlightInfo:
    """Structured flight information"""
    index: int
    price: Optional[str] = None
    airline: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: Optional[str] = None
    stops: str = "Unknown"
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    flight_number: Optional[str] = None
    co2_emissions: Optional[str] = None
    baggage_info: Optional[str] = None
    raw_text: Optional[str] = None

@dataclass
class RoundTripCombination:
    """Round trip combination data"""
    combination_id: int
    outbound_flight: FlightInfo
    return_flight: FlightInfo
    total_price: Optional[str] = None
    booking_url: Optional[str] = None
    timestamp: str = ""

# ==================== Enhanced Extraction Functions ====================

class FlightDataExtractor:
    """Enhanced flight data extraction with better parsing"""
    
    @staticmethod
    def extract_flight_data(soup: BeautifulSoup) -> List[Dict]:
        """Extract flight data with improved selectors and parsing"""
        flights = []
        
        # Enhanced selectors based on actual Google Flights structure
        flight_selectors = [
            '.pIav2d',  # Primary flight container
            '.gQ6yfe',  # Alternative container
            '[role="listitem"]',  # List items
            '.yR1fYc',   # Another flight class
            '.Ir0Voe',   # Flight card
            '[jsaction*="click"]',  # Clickable elements
        ]
        
        flight_elements = []
        for selector in flight_selectors:
            elements = soup.select(selector)
            if elements:
                flight_elements.extend(elements)
                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for elem in flight_elements:
            elem_id = id(elem)
            if elem_id not in seen:
                seen.add(elem_id)
                unique_elements.append(elem)
        
        for i, element in enumerate(unique_elements[:20]):  # Process up to 20 flights
            flight_info = FlightDataExtractor._parse_flight_element(element, i)
            if flight_info and (flight_info.get('price') or flight_info.get('airline')):
                flights.append(flight_info)
        
        return flights
    
    @staticmethod
    def _parse_flight_element(element, index: int) -> Dict:
        """Parse individual flight element with enhanced extraction"""
        flight_info = {}
        text_content = element.get_text(strip=True)
        
        if not text_content or len(text_content) < 10:
            return {}
        
        flight_info['raw_text'] = text_content
        
        # Price extraction with multiple patterns
        price_patterns = [
            r'\$[\d,]+',
            r'USD\s*[\d,]+',
            r'[\d,]+\s*dollars?'
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                flight_info['price'] = match.group()
                break
        
        # Time extraction - improved regex
        time_pattern = r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)'
        time_matches = re.findall(time_pattern, text_content)
        if time_matches:
            flight_info['times'] = time_matches
            if len(time_matches) >= 2:
                flight_info['departure_time'] = time_matches[0]
                flight_info['arrival_time'] = time_matches[1]
        
        # Duration extraction
        duration_patterns = [
            r'\d+\s*hr?\s*\d*\s*min?',
            r'\d+h\s*\d*m?'
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                flight_info['duration'] = match.group()
                break
        
        # Airline extraction - expanded list
        airlines = [
            'Spirit', 'American', 'Delta', 'United', 'Southwest', 
            'JetBlue', 'Alaska', 'Frontier', 'Hawaiian', 'Allegiant',
            'Sun Country', 'Breeze', 'Avelo'
        ]
        for airline in airlines:
            if airline.lower() in text_content.lower():
                flight_info['airline'] = airline
                break
        
        # Stops extraction
        if 'Nonstop' in text_content or 'nonstop' in text_content:
            flight_info['stops'] = 'Nonstop'
        elif '1 stop' in text_content:
            flight_info['stops'] = '1 stop'
        elif '2 stop' in text_content:
            flight_info['stops'] = '2 stops'
        
        # Airport codes
        airport_pattern = r'\b[A-Z]{3}\b'
        airports = re.findall(airport_pattern, text_content)
        if airports:
            flight_info['airports'] = airports
            if len(airports) >= 2:
                flight_info['departure_airport'] = airports[0]
                flight_info['arrival_airport'] = airports[1]
        
        # CO2 emissions
        co2_pattern = r'(\d+)\s*kg\s*CO2'
        co2_match = re.search(co2_pattern, text_content, re.IGNORECASE)
        if co2_match:
            flight_info['co2_emissions'] = co2_match.group()
        
        # Flight number
        flight_num_pattern = r'([A-Z]{2,3})\s*(\d{3,4})'
        flight_num_match = re.search(flight_num_pattern, text_content)
        if flight_num_match:
            flight_info['flight_number'] = flight_num_match.group()
        
        return flight_info

    @staticmethod
    def extract_detailed_flight_path(soup: BeautifulSoup) -> List[Dict]:
        """Extract detailed flight path information"""
        detailed_flights = []
        
        # Look for expanded flight details
        detail_selectors = [
            '[aria-expanded="true"]',
            '.expanded-content',
            '[data-expanded="true"]',
            '.flight-details-expanded'
        ]
        
        for selector in detail_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements[:10]:
                    details = FlightDataExtractor._parse_flight_details(elem)
                    if details:
                        detailed_flights.append(details)
        
        return detailed_flights
    
    @staticmethod
    def _parse_flight_details(element) -> Dict:
        """Parse detailed flight information"""
        details = {
            'segments': [],
            'total_duration': None,
            'layovers': []
        }
        
        text = element.get_text(strip=True)
        
        # Extract flight segments
        segment_pattern = r'([A-Z]{3})\s*→\s*([A-Z]{3})'
        segments = re.findall(segment_pattern, text)
        if segments:
            details['segments'] = [{'from': s[0], 'to': s[1]} for s in segments]
        
        # Extract layover information
        layover_pattern = r'(\d+\s*hr?\s*\d*\s*min?)\s*layover\s*in\s*([A-Z]{3})'
        layovers = re.findall(layover_pattern, text, re.IGNORECASE)
        if layovers:
            details['layovers'] = [{'duration': l[0], 'airport': l[1]} for l in layovers]
        
        return details if (details['segments'] or details['layovers']) else None

# ==================== Main Scraper Class ====================

class EnhancedFlightScraper:
    """Enhanced Google Flights scraper with all original functionality"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.extractor = FlightDataExtractor()
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
        
        launch_args = {
            'headless': self.config.headless,
            'slow_mo': self.config.slow_mo
        }
        
        if self.config.headless:
            # Additional args for headless mode
            launch_args['args'] = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        
        self.browser = await playwright.chromium.launch(**launch_args)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
    async def cleanup(self):
        """Clean up resources and files"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            
        if self.config.cleanup_files:
            self._cleanup_test_files()
            
    def _cleanup_test_files(self):
        """Remove generated test files"""
        patterns = [
            'flight_*.html',
            'flight_*.json',
            'error_*.html',
            'booking_*.html',
            'comprehensive_*.json',
            'sequential_*.json'
        ]
        
        for pattern in patterns:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    print(f"🗑️  Cleaned up: {file}")
                except:
                    pass
    
    async def search_and_extract(self, origin: str = "Louisville", 
                                destination: str = "Orlando",
                                departure_date: str = "Aug 10, 2025",
                                return_date: str = "Aug 12, 2025") -> Dict:
        """Main search function with comprehensive extraction"""
        results = {
            'search_params': {
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'return_date': return_date
            },
            'outbound_flights': [],
            'return_flights': [],
            'round_trip_combinations': [],
            'flight_details': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            print("🛫 Starting Enhanced Google Flights automation...")
            print("-" * 50)
            
            # Navigate to Google Flights
            print("Step 1: Navigating to Google Flights...")
            await self.page.goto("https://www.google.com/travel/flights")
            await self.page.wait_for_load_state('networkidle')
            
            # Fill search form
            await self._fill_search_form(origin, destination, departure_date, return_date)
            
            # Click search
            print("Step 6: Clicking Search button...")
            search_clicked = await self._click_search_button()
            
            if search_clicked:
                # Wait for results
                print("Step 7: Waiting for search results to load...")
                await self.page.wait_for_timeout(self.config.wait_medium)
                
                try:
                    await self.page.wait_for_selector('text="Search results"', timeout=5000)
                    print("✅ Search results section found")
                except:
                    print("⚠️  Search results section not found explicitly")
                
                # Extract flight data
                print("Step 8: Extracting flight data...")
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                flights = self.extractor.extract_flight_data(soup)
                results['outbound_flights'] = flights
                print(f"✅ Extracted {len(flights)} flights")
                
                # Save flight data
                if self.config.save_json and flights:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_file = f'flight_data_{timestamp}.json'
                    with open(json_file, 'w') as f:
                        json.dump(flights, f, indent=2)
                    print(f"💾 Flight data saved to '{json_file}'")
                
                # Click on flight details for more information
                if flights:
                    print(f"Step 9: Clicking flight details (first {self.config.max_flight_details})...")
                    details = await self._extract_flight_details()
                    results['flight_details'] = details
                
                # Try to get round trip combinations
                if self.config.max_combinations > 0 and len(flights) > 0:
                    print(f"Step 10: Extracting round trip combinations...")
                    combinations = await self._extract_round_trip_combinations(flights[:self.config.max_combinations])
                    results['round_trip_combinations'] = combinations
                    
            else:
                print("❌ Could not click search button")
                
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            if self.config.save_html:
                await self._save_error_page(str(e))
            
        return results
    
    async def _fill_search_form(self, origin: str, destination: str, 
                               departure_date: str, return_date: str):
        """Fill the search form with improved selectors"""
        
        # Set origin
        print(f"Step 2: Setting origin to {origin}...")
        origin_field = self.page.get_by_role('combobox', name='Where from?')
        await origin_field.click()
        await self.page.wait_for_timeout(self.config.wait_short)
        
        try:
            origin_search = self.page.get_by_role('combobox', name='Where else?')
            await origin_search.fill(origin)
            await self.page.wait_for_timeout(self.config.wait_short)
            
            # Try to click the first matching option
            await self.page.get_by_role('option', name=re.compile(origin, re.IGNORECASE)).first.click()
            print(f"✅ {origin} selected as origin")
        except:
            await self.page.keyboard.press('Enter')
            print(f"✅ {origin} entered as origin")
        
        # Set destination
        print(f"Step 3: Setting destination to {destination}...")
        dest_field = self.page.get_by_role('combobox', name='Where to?')
        await dest_field.click()
        await self.page.wait_for_timeout(self.config.wait_short)
        
        try:
            dest_search = self.page.get_by_role('combobox', name='Where to?')
            await dest_search.fill(destination)
            await self.page.wait_for_timeout(self.config.wait_short)
            
            await self.page.get_by_role('option', name=re.compile(destination, re.IGNORECASE)).first.click()
            print(f"✅ {destination} selected as destination")
        except:
            await self.page.keyboard.press('Enter')
            print(f"✅ {destination} entered as destination")
        
        # Set dates
        print(f"Step 4: Setting departure date to {departure_date}...")
        departure_field = self.page.get_by_role('textbox', name='Departure')
        await departure_field.click()
        await departure_field.fill(departure_date)
        
        print(f"Step 5: Setting return date to {return_date}...")
        return_field = self.page.get_by_role('textbox', name='Return')
        await return_field.click()
        await return_field.fill(return_date)
        
        # Close date picker
        await self.page.keyboard.press('Enter')
        await self.page.wait_for_timeout(self.config.wait_short)
        await self.page.keyboard.press('Enter')
        print("✅ Dates set and date picker closed")
        
    async def _click_search_button(self) -> bool:
        """Click search button with multiple strategies"""
        strategies = [
            lambda: self.page.get_by_role('button', name='Search').click(),
            lambda: self.page.locator('button:has-text("Search")').click(),
            lambda: self.page.keyboard.press('Enter'),
            lambda: self.page.get_by_role('button', name='Explore').click()
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                await strategy()
                print(f"✅ Search triggered using strategy {i+1}")
                return True
            except:
                continue
                
        return False
    
    async def _extract_flight_details(self) -> List[Dict]:
        """Extract detailed flight information by clicking detail buttons"""
        details = []
        
        try:
            # Find flight detail buttons
            detail_buttons = await self.page.query_selector_all('button[aria-label*="Flight details"]')
            
            if not detail_buttons:
                detail_buttons = await self.page.query_selector_all('button:has-text("Flight details")')
            
            print(f"Found {len(detail_buttons)} flight detail buttons")
            
            for i, button in enumerate(detail_buttons[:self.config.max_flight_details]):
                try:
                    is_visible = await button.is_visible()
                    if is_visible:
                        print(f"Clicking flight details button {i+1}...")
                        await button.click()
                        await self.page.wait_for_timeout(self.config.wait_short)
                        
                        # Extract expanded content
                        content = await self.page.content()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        detail_data = self.extractor.extract_detailed_flight_path(soup)
                        
                        if self.config.save_html:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            html_file = f'flight_detail_{i+1}_{timestamp}.html'
                            with open(html_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"💾 Detail HTML saved: {html_file}")
                        
                        if detail_data:
                            details.append({
                                'flight_index': i + 1,
                                'details': detail_data
                            })
                        
                        # Click again to collapse
                        try:
                            await button.click()
                            await self.page.wait_for_timeout(300)
                        except:
                            pass
                            
                except Exception as e:
                    print(f"⚠️  Error with detail button {i+1}: {e}")
                    
        except Exception as e:
            print(f"⚠️  Error extracting flight details: {e}")
            
        return details
    
    async def _extract_round_trip_combinations(self, outbound_flights: List[Dict]) -> List[Dict]:
        """Extract round trip combinations by clicking through flights"""
        combinations = []
        
        try:
            for i, outbound in enumerate(outbound_flights):
                print(f"\nProcessing outbound flight {i+1}/{len(outbound_flights)}")
                
                # Click on outbound flight
                flight_elements = await self.page.query_selector_all('.pIav2d, .gQ6yfe, [role="listitem"]')
                
                if i < len(flight_elements):
                    await flight_elements[i].click()
                    await self.page.wait_for_timeout(self.config.wait_medium)
                    
                    # Extract return flight options
                    return_content = await self.page.content()
                    return_soup = BeautifulSoup(return_content, 'html.parser')
                    return_flights = self.extractor.extract_flight_data(return_soup)
                    
                    if return_flights:
                        # Click first return flight
                        return_elements = await self.page.query_selector_all('.pIav2d, .gQ6yfe, [role="listitem"]')
                        if return_elements:
                            await return_elements[0].click()
                            await self.page.wait_for_timeout(self.config.wait_short)
                            
                            # Extract total price
                            final_content = await self.page.content()
                            total_price = self._extract_total_price(final_content)
                            
                            combination = {
                                'combination_id': i + 1,
                                'outbound': outbound,
                                'return_flight': return_flights[0],
                                'total_price': total_price
                            }
                            combinations.append(combination)
                            print(f"✅ Combination {i+1}: {total_price}")
                    
                    # Navigate back
                    await self.page.go_back()
                    await self.page.wait_for_timeout(self.config.wait_short)
                    await self.page.go_back()
                    await self.page.wait_for_timeout(self.config.wait_medium)
                    
        except Exception as e:
            print(f"⚠️  Error extracting combinations: {e}")
            
        return combinations
    
    def _extract_total_price(self, html: str) -> Optional[str]:
        """Extract total price from HTML with improved patterns"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try multiple strategies to find the total price
        
        # Strategy 1: Look for price in booking/confirmation elements
        price_selectors = [
            '[aria-label*="total price"]',
            '[aria-label*="Total"]',
            '.booking-total',
            '.price-total',
            '[data-price-total]',
            '.flt-subhead1.gws-flights-results__price',
            '.gws-flights-results__cheapest-price',
            '.gws-flights-results__price-total'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                price_match = re.search(r'\$[\d,]+', text)
                if price_match:
                    return price_match.group()
        
        # Strategy 2: Look for price patterns in text
        text = soup.get_text()
        patterns = [
            r'Total[:\s]*\$[\d,]+',
            r'\$[\d,]+\s*(?:total|round trip)',
            r'(?:Round trip|Total price)[:\s]*\$[\d,]+',
            r'Book for \$[\d,]+',
            r'Continue to book.*?\$[\d,]+',
            r'Price[:\s]*\$[\d,]+.*?(?:round trip|total)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_match = re.search(r'\$[\d,]+', match.group())
                if price_match:
                    return price_match.group()
        
        # Strategy 3: Find all prices and get the largest one (likely total)
        all_prices = re.findall(r'\$[\d,]+', text)
        if all_prices:
            # Convert to integers for comparison
            price_values = []
            for price in all_prices:
                try:
                    value = int(price.replace('$', '').replace(',', ''))
                    price_values.append((value, price))
                except:
                    pass
            
            if price_values:
                # Return the largest price (likely the total)
                price_values.sort(reverse=True)
                return price_values[0][1]
        
        return None
    
    async def _save_error_page(self, error_msg: str):
        """Save error page for debugging"""
        try:
            content = await self.page.content()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = f'error_page_{timestamp}.html'
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Error: {error_msg} -->\n{content}")
            print(f"💾 Error page saved: {error_file}")
        except:
            pass

# ==================== Main Execution ====================

async def main():
    """Main execution function"""
    config = ScraperConfig(
        headless=False,  # Set to True for production
        slow_mo=100,     # Faster than original
        max_flight_details=5,
        max_combinations=3,
        cleanup_files=False,  # Keep files for inspection
        save_html=True,
        save_json=True
    )
    
    async with EnhancedFlightScraper(config) as scraper:
        results = await scraper.search_and_extract(
            origin="Louisville",
            destination="Orlando",
            departure_date="Aug 10, 2025",
            return_date="Aug 12, 2025"
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("🎯 SEARCH RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Flights found: {len(results['outbound_flights'])}")
        if results['outbound_flights']:
            print("\nTop 5 flights by price:")
            sorted_flights = sorted(results['outbound_flights'], 
                                  key=lambda x: int(re.sub(r'[^\d]', '', x.get('price', '99999'))))
            
            for i, flight in enumerate(sorted_flights[:5], 1):
                print(f"{i}. {flight.get('airline', 'Unknown')} - {flight.get('price', 'N/A')}")
                print(f"   {flight.get('departure_time', 'N/A')} → {flight.get('arrival_time', 'N/A')}")
                print(f"   Duration: {flight.get('duration', 'N/A')}, Stops: {flight.get('stops', 'N/A')}")
        
        if results['round_trip_combinations']:
            print(f"\n💼 Round trip combinations: {len(results['round_trip_combinations'])}")
            for combo in results['round_trip_combinations']:
                print(f"   Combination {combo['combination_id']}: {combo.get('total_price', 'N/A')}")
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f'comprehensive_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Complete results saved to: {results_file}")

if __name__ == "__main__":
    import time
    start_time = time.time()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Script interrupted by user")
    except Exception as e:
        print(f"❌ Script failed: {e}")
    finally:
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed:.2f} seconds")