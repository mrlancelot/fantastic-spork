#!/usr/bin/env python3
"""
Google Flights Round-Trip Scraper - Enhanced Version
Extracts detailed round-trip information for multiple flight options
Provides users with 3-4 different flight choices with complete details
"""

import asyncio
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random



class FlightDataExtractor:
    """Utilities for extracting and cleaning flight data"""
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing special characters"""
        if not text:
            return ""
        return text.replace('\u202f', ' ').replace('\xa0', ' ').strip()
    @staticmethod
    def extract_price(text: str) -> Optional[str]:
        """Extract price from text - handles multiple currencies"""

        patterns = [
            r'[\$\£\€\¥\₹\₽\₩][\d,]+(?:\.\d{2})?',
            r'[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|JPY|INR|KRW|CNY|AUD|CAD)',
            r'(?:USD|EUR|GBP|JPY|INR|KRW|CNY|AUD|CAD)\s*[\d,]+(?:\.\d{2})?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()

        match = re.search(r'\b\d{3,}(?:,\d{3})*(?:\.\d{2})?\b', text)
        return match.group() if match else None
    @staticmethod
    def extract_price_value(price_str: str) -> int:
        """Convert price string to integer value for comparison"""
        if not price_str:
            return 999999

        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:

            return int(float(cleaned))
        except (ValueError, AttributeError):
            return 999999
    @staticmethod
    def extract_times(text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract departure and arrival times"""
        text = FlightDataExtractor.clean_text(text)
        times = re.findall(r'\d{1,2}:\d{2}\s*(?:AM|PM)', text)

        seen = set()
        unique_times = []
        for time in times:
            if time not in seen:
                seen.add(time)
                unique_times.append(time)
        departure = unique_times[0] if len(unique_times) > 0 else None
        arrival = unique_times[1] if len(unique_times) > 1 else None
        return departure, arrival
    @staticmethod
    def extract_duration(text: str) -> Optional[str]:
        """Extract flight duration"""
        patterns = [
            r'(\d+\s*hr?\s*\d*\s*min?)',
            r'(\d+h\s*\d*m?)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None
    @staticmethod
    def extract_airline(text: str) -> Optional[str]:
        """Extract airline name - handles any airline globally"""

        airline_indicators = ['airlines', 'airways', 'air ', 'fly', 'jet', 'aviation', 'express']

        words = text.split()

        for i, word in enumerate(words):
            word_lower = word.lower()

            for indicator in airline_indicators:
                if indicator in word_lower:

                    if i > 0:

                        airline_name = words[i-1] + ' ' + word
                        return airline_name.strip()
                    else:
                        return word.strip()

            if word_lower in ['united', 'delta', 'american', 'southwest', 'spirit',
                             'frontier', 'alaska', 'hawaiian', 'emirates', 'qatar',
                             'lufthansa', 'klm', 'ana', 'jal', 'ryanair', 'easyjet',
                             'vueling', 'wizz', 'pegasus', 'indigo', 'spicejet']:
                return word.capitalize()


        capitalized_words = [w for w in words if w and w[0].isupper() and len(w) > 2]

        for i, word in enumerate(capitalized_words):
            if i < len(capitalized_words) - 1:
                next_word = capitalized_words[i + 1].lower()
                if any(ind in next_word for ind in ['air', 'airlines', 'airways']):
                    return f"{word} {capitalized_words[i + 1]}"
        return None
    @staticmethod
    def extract_stops(text: str) -> str:
        """Extract stop information"""
        text_lower = text.lower()
        if 'nonstop' in text_lower:
            return 'Nonstop'
        elif '2 stop' in text_lower:
            return '2 stops'
        elif '1 stop' in text_lower:
            return '1 stop'
        return 'Unknown'
    @staticmethod
    def extract_layover_info(text: str) -> Optional[Dict]:
        """Extract layover airport and duration"""

        match = re.search(r'(\d+\s*hr?\s*\d*\s*min?)\s+in\s+([A-Z]{3})', text)
        if match:
            return {
                'duration': match.group(1),
                'airport': match.group(2)
            }
        return None
    @staticmethod
    def extract_airports(text: str, search_origin: Optional[str] = None, search_destination: Optional[str] = None) -> Tuple[str, str]:
        """Extract origin and destination airport codes - fully dynamic
        Args:
            text: Text to extract from
            search_origin: The actual origin code from search params
            search_destination: The actual destination code from search params
        Returns:
            Tuple of (origin, destination) - always returns the search params if provided
        """

        origin = search_origin if search_origin else 'N/A'
        destination = search_destination if search_destination else 'N/A'

        if not search_origin or not search_destination:

            codes = re.findall(r'\b[A-Z]{3,4}\b', text)

            route_pattern = re.search(r'\b([A-Z]{3,4})\s*(?:to|-|→|>)\s*([A-Z]{3,4})\b', text)
            if route_pattern:
                if not search_origin:
                    origin = route_pattern.group(1)
                if not search_destination:
                    destination = route_pattern.group(2)
            elif len(codes) >= 2:

                if not search_origin:
                    origin = codes[0]
                if not search_destination:
                    destination = codes[1]
            elif len(codes) == 1:

                if not search_origin:
                    origin = codes[0]
        return origin, destination

class GoogleFlightsRoundTripScraper:
    """Google Flights scraper for multiple round-trip flight options"""
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.extractor = FlightDataExtractor()
    async def search_round_trip_options(self, 
                                       origin: str = "Louisville",
                                       destination: str = "Orlando",
                                       departure_date: str = "Aug 10, 2025",
                                       return_date: str = "Aug 12, 2025",
                                       num_options: int = 10) -> Dict:
        """
        Search for round-trip flights and extract detailed information for multiple options
        Args:
            origin: Origin city
            destination: Destination city
            departure_date: Departure date
            return_date: Return date
            num_options: Number of flight options to get details for (default: 4)
        Returns:
            Dictionary containing multiple flight options with details
        """
        async with async_playwright() as p:
            print(f"🖥️  Launching browser (headless={self.headless})...")
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=200
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            result = {
                'search_params': {
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date,
                    'return_date': return_date
                },
                'flight_options': [],
                'summary': {},
                'timestamp': datetime.now().isoformat()
            }
            try:
                print(f"🛫 Searching round-trip flights: {origin} ↔ {destination}")
                print(f"📅 Dates: {departure_date} - {return_date}")
                print(f"🎯 Getting details for top {num_options} flight options")
                print("-" * 60)

                print("Step 1: Opening Google Flights...")
                await page.goto("https://www.google.com/travel/flights")
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                print(f"Step 2: Setting origin to {origin}...")
                origin_field = page.get_by_role('combobox', name='Where from?')
                await origin_field.click()
                await asyncio.sleep(0.5)
                origin_search = page.get_by_role('combobox', name='Where else?')
                await origin_search.fill(origin)
                await asyncio.sleep(1)
                await page.keyboard.press('Enter')
                await asyncio.sleep(1)

                print(f"Step 3: Setting destination to {destination}...")
                dest_field = page.get_by_role('combobox', name='Where to?')
                await dest_field.click()
                await asyncio.sleep(0.5)
                dest_search = page.get_by_role('combobox', name='Where to?')
                await dest_search.fill(destination)
                await asyncio.sleep(1)
                await page.keyboard.press('Enter')
                await asyncio.sleep(1)

                print(f"Step 4: Setting departure date to {departure_date}...")
                departure_field = page.get_by_role('textbox', name='Departure')
                await departure_field.click()
                await departure_field.fill(departure_date)
                await asyncio.sleep(0.5)

                print(f"Step 5: Setting return date to {return_date}...")
                return_field = page.get_by_role('textbox', name='Return')
                await return_field.click()
                await return_field.fill(return_date)
                await asyncio.sleep(0.5)

                await page.keyboard.press('Enter')
                await asyncio.sleep(0.5)
                await page.keyboard.press('Enter')
                await asyncio.sleep(1)

                print("Step 6: Searching for flights...")
                search_button = page.get_by_role('button', name='Search')
                if await search_button.is_visible():
                    await search_button.click()
                else:
                    await page.keyboard.press('Enter')

                print("Step 7: Waiting for results...")
                await page.wait_for_timeout(5000)

                search_url = page.url

                print("Step 8: Extracting flight data...")
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                all_flights = self._extract_flights_from_page(soup, origin, destination)
                print(f"✅ Found {len(all_flights)} total flights")

                print(f"\nStep 9: Getting detailed round-trip information for top {num_options} options...")


                if num_options >= 10:
                    selected_flights = all_flights[:min(num_options, len(all_flights))]
                else:

                    flight_groups = self._categorize_flights(all_flights)
                    selected_flights = self._select_diverse_options(flight_groups, num_options)
                for i, flight in enumerate(selected_flights[:num_options]):
                    print(f"\n  Option {i+1}: {flight.get('airline')} - {flight.get('price')} ({flight.get('stops')})")
                    print(f"    (Flight index: {flight.get('index')})")

                    option = {
                        'option_number': i + 1,
                        'basic_info': flight,
                        'outbound': {
                            'airline': flight.get('airline'),
                            'price': flight.get('price'),
                            'departure_time': flight.get('departure_time'),
                            'arrival_time': flight.get('arrival_time'),
                            'duration': flight.get('duration'),
                            'stops': flight.get('stops'),
                            'origin': flight.get('origin_airport'),
                            'destination': flight.get('destination_airport')
                        },
                        'return': {
                            'note': 'Return flight will be selected based on availability',
                            'typical_price_included': True
                        },
                        'total_price': flight.get('price'),
                        'emissions': flight.get('emissions')
                    }

                    try:

                        await page.goto(search_url)
                        await page.wait_for_timeout(2500)

                        await page.wait_for_selector('.pIav2d, .yR1fYc, .Rk10dc', timeout=5000)


                        flight_elements = await page.query_selector_all('.pIav2d')
                        if not flight_elements or len(flight_elements) < 5:
                            flight_elements = await page.query_selector_all('.yR1fYc')
                        if not flight_elements or len(flight_elements) < 5:
                            flight_elements = await page.query_selector_all('.Rk10dc')
                        if not flight_elements or len(flight_elements) < 5:

                            all_elements = await page.query_selector_all('[role="listitem"]')
                            flight_elements = []
                            for elem in all_elements:
                                text = await elem.inner_text()

                                if '$' in text and ('AM' in text or 'PM' in text):
                                    flight_elements.append(elem)

                        element_index = min(i, len(flight_elements) - 1)
                        if flight_elements and element_index >= 0:
                            print(f"    Clicking on flight card {element_index + 1} of {len(flight_elements)}")
                            await flight_elements[element_index].click()
                            await page.wait_for_timeout(3000)

                            content = await page.content()
                            soup = BeautifulSoup(content, 'html.parser')
                            return_flights = self._extract_return_flights(soup)
                            if return_flights and len(return_flights) > 0:

                                best_return = return_flights[0]
                                option['return'] = {
                                    'departure_time': best_return.get('departure_time', 'TBD'),
                                    'arrival_time': best_return.get('arrival_time', 'TBD'),
                                    'duration': best_return.get('duration', 'TBD'),
                                    'stops': best_return.get('stops', 'TBD'),
                                    'airline': best_return.get('airline', flight.get('airline')),
                                    'options_available': len(return_flights)
                                }
                                print(f"    Found {len(return_flights)} return flight options")
                            else:

                                option['return'] = {
                                    'note': 'Return flight details will be shown at booking',
                                    'typical_price_included': True
                                }
                    except Exception as e:
                        print(f"    Note: Return details pending")
                        option['return'] = {
                            'note': 'Return flight details available at booking',
                            'typical_price_included': True
                        }
                    result['flight_options'].append(option)

                result['summary'] = self._generate_summary(result['flight_options'])
                print(f"\n✅ Successfully extracted {len(result['flight_options'])} flight options with details")
            except Exception as e:
                print(f"❌ Error: {e}")
                result['error'] = str(e)
            finally:
                await browser.close()
            return result
    def _extract_flights_from_page(self, soup, search_origin: Optional[str] = None, search_destination: Optional[str] = None) -> List[Dict]:
        """Extract all flight information from search results page
        Args:
            soup: BeautifulSoup object of the page
            search_origin: The actual origin airport code being searched
            search_destination: The actual destination airport code being searched
        """
        flights = []
        try:

            flight_selectors = [
                '.pIav2d',
                '.yR1fYc',
                '[role="listitem"]',
                '.Ir0Voe'
            ]
            flight_elements = []
            for selector in flight_selectors:
                elements = soup.select(selector)
                if elements:
                    flight_elements = elements
                    break
            for i, element in enumerate(flight_elements[:30]):
                text = self.extractor.clean_text(element.get_text(strip=True))
                if not text:
                    continue

                price = self.extractor.extract_price(text)
                if not price:
                    continue
                departure_time, arrival_time = self.extractor.extract_times(text)
                origin, dest = self.extractor.extract_airports(text, search_origin, search_destination)

                airline = self.extractor.extract_airline(text)

                if not airline:
                    img_tags = element.select('img[alt]')
                    for img in img_tags:
                        alt_text = img.get('alt', '')
                        if 'airline' in alt_text.lower() or 'airways' in alt_text.lower():
                            airline = self.extractor.extract_airline(alt_text)
                            if airline:
                                break

                if not airline:

                    potential_codes = re.findall(r'\b[A-Z]{2}\b', text)
                    if potential_codes:

                        airline = f"Airline {potential_codes[0]}"

                if not airline:
                    operated_pattern = re.search(r'(?:Operated by|by)\s+([A-Za-z\s]+?)(?:\.|,|$)', text)
                    if operated_pattern:
                        airline = operated_pattern.group(1).strip()

                flight = {
                    'index': i + 1,
                    'price': price,
                    'price_value': self.extractor.extract_price_value(price),
                    'airline': airline if airline else f'Flight Option {i+1}',
                    'departure_time': departure_time if departure_time else 'Check Details',
                    'arrival_time': arrival_time if arrival_time else 'Check Details',
                    'duration': self.extractor.extract_duration(text) or 'See Details',
                    'stops': self.extractor.extract_stops(text),
                    'origin_airport': origin,
                    'destination_airport': dest,
                    'raw_text': text[:200] if len(text) > 200 else text
                }

                if flight['stops'] != 'Nonstop':
                    layover = self.extractor.extract_layover_info(text)
                    if layover:
                        flight['layover'] = layover

                emissions_match = re.search(r'(\d+)\s*kg\s*CO2', text)
                if emissions_match:
                    flight['emissions'] = f"{emissions_match.group(1)} kg CO2"
                flights.append(flight)
        except Exception as e:
            print(f"Error extracting flights: {e}")

        flights.sort(key=lambda x: x['price_value'])
        return flights
    def _extract_return_flights(self, soup) -> List[Dict]:
        """Extract return flight options from the page"""
        return_flights = []
        try:



            all_flight_cards = soup.select('.pIav2d, .yR1fYc, .Rk10dc')

            return_section_found = False
            for i, card in enumerate(all_flight_cards):
                card_text = card.get_text(strip=True).lower()

                if not return_section_found:

                    parent_text = card.parent.get_text(strip=True).lower() if card.parent else ""
                    if 'return' in parent_text or 'select' in parent_text or i > len(all_flight_cards) // 2:
                        return_section_found = True

                if return_section_found:
                    text = self.extractor.clean_text(card.get_text(strip=True))
                    if len(text) < 20:
                        continue
                    departure_time, arrival_time = self.extractor.extract_times(text)
                    duration = self.extractor.extract_duration(text)
                    if departure_time and arrival_time:
                        return_flight = {
                            'departure_time': departure_time,
                            'arrival_time': arrival_time,
                            'duration': duration if duration else 'N/A',
                            'stops': self.extractor.extract_stops(text),
                            'airline': self.extractor.extract_airline(text) or 'Multiple'
                        }

                        is_duplicate = False
                        for existing in return_flights:
                            if (existing['departure_time'] == return_flight['departure_time'] and 
                                existing['arrival_time'] == return_flight['arrival_time']):
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            return_flights.append(return_flight)
                            if len(return_flights) >= 5:
                                break

            if not return_flights:

                all_elements = soup.find_all(text=re.compile(r'\d{1,2}:\d{2}\s*(?:AM|PM)'))
                mid_point = len(all_elements) // 2
                for elem in all_elements[mid_point:]:
                    parent = elem.parent
                    if parent:
                        text = self.extractor.clean_text(parent.get_text(strip=True))
                        departure_time, arrival_time = self.extractor.extract_times(text)
                        if departure_time and arrival_time:
                            return_flight = {
                                'departure_time': departure_time,
                                'arrival_time': arrival_time,
                                'duration': self.extractor.extract_duration(text) or 'N/A',
                                'stops': self.extractor.extract_stops(text),
                                'airline': self.extractor.extract_airline(text) or 'Various'
                            }

                            is_duplicate = any(
                                existing['departure_time'] == return_flight['departure_time'] and 
                                existing['arrival_time'] == return_flight['arrival_time']
                                for existing in return_flights
                            )
                            if not is_duplicate:
                                return_flights.append(return_flight)
                                if len(return_flights) >= 3:
                                    break
        except Exception as e:
            print(f"    Debug: Error in return flight extraction: {e}")
        return return_flights
    def _categorize_flights(self, flights: List[Dict]) -> Dict:
        """Categorize flights by different characteristics"""
        categories = {
            'cheapest': [],
            'nonstop': [],
            'one_stop': [],
            'morning': [],
            'afternoon': [],
            'evening': [],
            'by_airline': {}
        }
        for flight in flights:

            categories['cheapest'].append(flight)

            if flight.get('stops') == 'Nonstop':
                categories['nonstop'].append(flight)
            elif flight.get('stops') == '1 stop':
                categories['one_stop'].append(flight)

            dep_time = flight.get('departure_time', '')
            if dep_time:
                hour = self._extract_hour(dep_time)
                if 5 <= hour < 12:
                    categories['morning'].append(flight)
                elif 12 <= hour < 17:
                    categories['afternoon'].append(flight)
                else:
                    categories['evening'].append(flight)

            airline = flight.get('airline', 'Unknown')
            if airline not in categories['by_airline']:
                categories['by_airline'][airline] = []
            categories['by_airline'][airline].append(flight)
        return categories
    def _select_diverse_options(self, categories: Dict, num_options: int) -> List[Dict]:
        """Select diverse flight options for users"""
        selected = []
        seen_combinations = set()

        if categories['cheapest']:
            flight = categories['cheapest'][0]
            key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
            selected.append(flight)
            seen_combinations.add(key)

        if categories['nonstop'] and len(selected) < num_options:
            for flight in categories['nonstop'][:3]:
                key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
                if key not in seen_combinations:
                    selected.append(flight)
                    seen_combinations.add(key)
                    break

        if categories['morning'] and len(selected) < num_options:
            for flight in categories['morning'][:3]:
                key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
                if key not in seen_combinations:
                    selected.append(flight)
                    seen_combinations.add(key)
                    break

        if categories['afternoon'] and len(selected) < num_options:
            for flight in categories['afternoon'][:3]:
                key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
                if key not in seen_combinations:
                    selected.append(flight)
                    seen_combinations.add(key)
                    break

        airlines_added = set()
        for airline, flights in categories['by_airline'].items():
            if len(selected) >= num_options:
                break
            if airline not in airlines_added and flights:
                flight = flights[0]
                key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
                if key not in seen_combinations:
                    selected.append(flight)
                    seen_combinations.add(key)
                    airlines_added.add(airline)

        if categories['one_stop'] and len(selected) < num_options:
            for flight in categories['one_stop'][:5]:
                if len(selected) >= num_options:
                    break
                key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
                if key not in seen_combinations:
                    selected.append(flight)
                    seen_combinations.add(key)

        for flight in categories['cheapest'][1:]:
            if len(selected) >= num_options:
                break
            key = f"{flight.get('airline')}_{flight.get('stops')}_{flight.get('price')}"
            if key not in seen_combinations:
                selected.append(flight)
                seen_combinations.add(key)
        return selected[:num_options]
    def _extract_hour(self, time_str: str) -> int:
        """Extract hour from time string like '10:30 AM'"""
        try:
            match = re.search(r'(\d{1,2}):\d{2}\s*(AM|PM)', time_str)
            if match:
                hour = int(match.group(1))
                period = match.group(2)
                if period == 'PM' and hour != 12:
                    hour += 12
                elif period == 'AM' and hour == 12:
                    hour = 0
                return hour
        except:
            pass
        return 12
    def _generate_summary(self, options: List[Dict]) -> Dict:
        """Generate summary statistics for the flight options"""
        if not options:
            return {}
        prices = [opt['basic_info']['price_value'] for opt in options if opt.get('basic_info')]
        nonstop_count = sum(1 for opt in options if opt['basic_info'].get('stops') == 'Nonstop')
        airlines = list(set(opt['basic_info'].get('airline', 'Unknown') for opt in options if opt.get('basic_info')))
        return {
            'total_options': len(options),
            'price_range': {
                'min': f"${min(prices):,}" if prices else None,
                'max': f"${max(prices):,}" if prices else None
            },
            'nonstop_available': nonstop_count > 0,
            'airlines_included': airlines
        }
    def display_results(self, result: Dict) -> None:
        """Display the search results in a user-friendly format"""
        print("\n" + "="*80)
        print("ROUND-TRIP FLIGHT OPTIONS")
        print("="*80)

        params = result.get('search_params', {})
        print(f"\n📍 Route: {params.get('origin')} ↔ {params.get('destination')}")
        print(f"📅 Dates: {params.get('departure_date')} - {params.get('return_date')}")

        options = result.get('flight_options', [])
        if options:
            print(f"\n✈️ Found {len(options)} flight options for you:\n")
            for option in options:
                print(f"{'='*60}")
                print(f"OPTION {option.get('option_number')}")
                print(f"{'='*60}")
                basic = option.get('basic_info', {})
                outbound = option.get('outbound', {})

                print(f"💰 TOTAL PRICE: {basic.get('price', 'N/A')} round-trip")

                print(f"✈️  Airline: {basic.get('airline', 'Unknown')}")
                print(f"🛬 Stops: {basic.get('stops', 'Unknown')}")

                print(f"\n🛫 OUTBOUND:")
                print(f"   Departure: {outbound.get('departure_time', 'N/A')}")
                print(f"   Arrival: {outbound.get('arrival_time', 'N/A')}")
                print(f"   Duration: {outbound.get('duration', 'N/A')}")
                print(f"   Route: {outbound.get('origin', 'SDF')} → {outbound.get('destination', 'MCO')}")

                if basic.get('layover'):
                    layover = basic['layover']
                    print(f"   Layover: {layover.get('duration')} in {layover.get('airport')}")

                ret = option.get('return', {})
                print(f"\n🛬 RETURN:")
                if ret.get('departure_time'):
                    print(f"   Departure: {ret.get('departure_time', 'N/A')}")
                    print(f"   Arrival: {ret.get('arrival_time', 'N/A')}")
                    print(f"   Duration: {ret.get('duration', 'N/A')}")
                    print(f"   Stops: {ret.get('stops', 'N/A')}")
                    if ret.get('options_available') and ret['options_available'] > 1:
                        print(f"   ({ret['options_available']} return options available)")
                elif ret.get('note'):
                    print(f"   {ret.get('note')}")
                else:
                    print(f"   Return flights available at booking")

                if basic.get('emissions'):
                    print(f"\n🌍 Carbon: {basic['emissions']}")
                print()

        summary = result.get('summary', {})
        if summary:
            print("-"*60)
            print("SUMMARY")
            print("-"*60)
            if summary.get('price_range'):
                print(f"💵 Price range: {summary['price_range']['min']} - {summary['price_range']['max']}")
            if summary.get('nonstop_available'):
                print(f"✈️  Nonstop flights available")
            if summary.get('airlines_included'):
                print(f"🛩️  Airlines: {', '.join(summary['airlines_included'])}")
