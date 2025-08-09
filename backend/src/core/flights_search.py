#!/usr/bin/env python3
"""
Comprehensive Google Flights Round Trip Search
Searches for flights, extracts detailed data, and gets actual round trip pricing
for multiple combinations of outbound and return flights.

Features:
- Extracts top flight options with detailed information
- Gets actual round trip totals by navigating through booking flow
- Handles Google Flights navigation patterns (double back for totals)
- Comprehensive data extraction and display
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import time
import random
import json
from bs4 import BeautifulSoup

def extract_round_trip_total_after_back(soup):
    """
    Extract round trip total after going back twice
    The second amount shown is the actual round trip price
    """
    try:
        page_text = soup.get_text()
        import re
        
        # Look for round trip price patterns
        round_trip_patterns = [
            r'round\s*trip[:\s]*\$[\d,]+',
            r'\$[\d,]+\s*round\s*trip',
            r'Total[:\s]*\$[\d,]+',
            r'\$[\d,]+\s*total'
        ]
        
        for pattern in round_trip_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                price_match = re.search(r'\$[\d,]+', match.group())
                if price_match:
                    return price_match.group()
        
        # Fallback: look for all prices and return the most likely total
        prices = re.findall(r'\$[\d,]+', page_text)
        if prices:
            # Convert to integers for comparison
            price_values = []
            for price in prices:
                try:
                    value = int(price.replace('$', '').replace(',', ''))
                    price_values.append((value, price))
                except:
                    continue
            
            if price_values:
                # Sort by value and return the largest (likely the total)
                price_values.sort(key=lambda x: x[0], reverse=True)
                return price_values[0][1]
            
    except Exception as e:
        print(f"Error extracting round trip total: {e}")
    
    return None

def extract_flight_options(soup):
    """
    Extract flight options from current page with enhanced details
    """
    flights = []
    
    try:
        # Look for flight listings
        flight_selectors = [
            '.gQ6yfe',  # Main flight container
            '[role="listitem"]',
            '.pIav2d',
            '.yR1fYc', 
            '.Ir0Voe',
            '[data-testid*="flight"]'
        ]
        
        flight_elements = []
        for selector in flight_selectors:
            elements = soup.select(selector)
            if elements:
                flight_elements.extend(elements)
                break
        
        for i, element in enumerate(flight_elements[:10]):  # Limit to first 10
            flight_info = {
                'index': i + 1,
                'element_id': f'flight_{i+1}'
            }
            
            text_content = element.get_text(strip=True)
            if text_content:
                flight_info['raw_text'] = text_content
                import re
                
                # Extract price
                price_match = re.search(r'\$[\d,]+', text_content)
                if price_match:
                    flight_info['price'] = price_match.group()
                
                # Extract times
                time_matches = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', text_content)
                if time_matches:
                    flight_info['departure_time'] = time_matches[0] if len(time_matches) > 0 else None
                    flight_info['arrival_time'] = time_matches[1] if len(time_matches) > 1 else None
                    flight_info['all_times'] = time_matches
                
                # Extract duration
                duration_match = re.search(r'\d+h\s*\d*m?|\d+\s*hr\s*\d*\s*min', text_content)
                if duration_match:
                    flight_info['duration'] = duration_match.group()
                
                # Extract airline
                airline_patterns = ['United', 'Delta', 'American', 'Southwest', 'JetBlue', 'Alaska', 'Spirit', 'Frontier']
                for airline in airline_patterns:
                    if airline.lower() in text_content.lower():
                        flight_info['airline'] = airline
                        break
                
                # Check for stops
                if 'Nonstop' in text_content:
                    flight_info['stops'] = 'Nonstop'
                elif '1 stop' in text_content:
                    flight_info['stops'] = '1 stop'
                elif '2 stop' in text_content:
                    flight_info['stops'] = '2 stops'
            
            flights.append(flight_info)
    
    except Exception as e:
        print(f"Error extracting flight options: {e}")
    
    return flights

def extract_flight_data(soup):
    """
    Extract flight data from Google Flights HTML using BeautifulSoup
    """
    flights = []
    
    try:
        # Look for flight listings with multiple selectors
        flight_selectors = [
            '.gQ6yfe',  # Main flight container
            '[role="listitem"]',
            '.pIav2d',
            '.yR1fYc', 
            '.Ir0Voe',
            '[data-testid*="flight"]'
        ]
        
        flight_elements = []
        for selector in flight_selectors:
            elements = soup.select(selector)
            if elements:
                flight_elements.extend(elements)
                break
        
        for i, element in enumerate(flight_elements[:20]):  # Limit to first 20
            flight_info = {}
            text_content = element.get_text(strip=True)
            if text_content:
                flight_info['raw_text'] = text_content
                import re
                
                # Extract price
                price_match = re.search(r'\$[\d,]+', text_content)
                if price_match:
                    flight_info['price'] = price_match.group()
                
                # Extract times
                time_matches = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', text_content)
                if time_matches:
                    flight_info['times'] = time_matches
                
                # Extract duration
                duration_match = re.search(r'\d+h\s*\d*m?', text_content)
                if duration_match:
                    flight_info['duration'] = duration_match.group()
                
                # Extract airline
                airline_patterns = ['United', 'Delta', 'American', 'Southwest', 'JetBlue', 'Alaska', 'Spirit', 'Frontier']
                for airline in airline_patterns:
                    if airline.lower() in text_content.lower():
                        flight_info['airline'] = airline
                        break
            
            if element.get('data-testid'):
                flight_info['data_testid'] = element.get('data-testid')
            
            if flight_info:
                flights.append(flight_info)
    
    except Exception as e:
        print(f"Error extracting flight data: {e}")
    
    return flights
    
def extract_return_flight_data(soup):
    """
    Extract return flight options from the return flight selection page
    """
    return_flights = []
    
    try:
        # Look for return flight listings
        flight_selectors = [
            '.gQ6yfe',  # Main flight container
            '[role="listitem"]',
            '.flight-option',
            '[data-testid*="flight"]'
        ]
        
        flight_elements = []
        for selector in flight_selectors:
            elements = soup.select(selector)
            if elements:
                flight_elements = elements
                break
        
        for i, element in enumerate(flight_elements[:10]):  # Limit to first 10
            return_flight = {
                'return_flight_index': i + 1,
                'direction': 'return'
            }
            
            text_content = element.get_text(strip=True)
            if text_content:
                return_flight['raw_text'] = text_content
                
                import re
                # Extract flight details
                times = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', text_content)
                if times:
                    return_flight['departure_time'] = times[0] if len(times) > 0 else None
                    return_flight['arrival_time'] = times[1] if len(times) > 1 else None
                    return_flight['all_times'] = times
                
                # Extract duration
                duration_match = re.search(r'\d+\s*hr?\s*\d*\s*min?', text_content)
                if duration_match:
                    return_flight['duration'] = duration_match.group()
                
                # Extract airline
                airline_patterns = ['American', 'Delta', 'United', 'Southwest', 'JetBlue', 'Alaska', 'Spirit', 'Frontier']
                for airline in airline_patterns:
                    if airline.lower() in text_content.lower():
                        return_flight['airline'] = airline
                        break
                
                # Extract airport codes
                airport_codes = re.findall(r'\b[A-Z]{3}\b', text_content)
                if len(airport_codes) >= 2:
                    return_flight['origin_airport'] = airport_codes[0]
                    return_flight['destination_airport'] = airport_codes[1]
                
                # Extract stops/layovers
                if 'nonstop' in text_content.lower():
                    return_flight['stops'] = 0
                    return_flight['stop_type'] = 'Nonstop'
                elif '1 stop' in text_content.lower():
                    return_flight['stops'] = 1
                    return_flight['stop_type'] = '1 stop'
                    # Extract layover info
                    layover_match = re.search(r'(\d+\s*hr?\s*\d*\s*min?).*?([A-Z]{3})', text_content)
                    if layover_match:
                        return_flight['layover_duration'] = layover_match.group(1)
                        return_flight['layover_airport'] = layover_match.group(2)
                
                # Extract price
                price_match = re.search(r'\$[\d,]+', text_content)
                if price_match:
                    return_flight['price'] = price_match.group()
            
            if return_flight.get('departure_time') or return_flight.get('airline'):
                return_flights.append(return_flight)
    
    except Exception as e:
        print(f"Error extracting return flight data: {e}")
    
    return return_flights

def extract_booking_summary_data(soup):
    """
    Extract complete round-trip flight details from the final booking summary page
    """
    booking_data = {
        'outbound_flight': {},
        'return_flight': {},
        'total_price': None,
        'booking_details': {}
    }
    
    try:
        text_content = soup.get_text()
        
        # Extract total price
        import re
        price_match = re.search(r'\$\d{3,4}', text_content)
        if price_match:
            booking_data['total_price'] = price_match.group()
        
        # Look for flight segments in the booking summary
        flight_segments = soup.select('li, .flight-segment, [data-testid*="flight"]')
        
        outbound_found = False
        return_found = False
        
        for segment in flight_segments:
            segment_text = segment.get_text(strip=True)
            
            # Check if this is outbound or return flight
            if any(keyword in segment_text.lower() for keyword in ['departing', 'sun, aug 10', 'sdf', 'louisville']):
                if not outbound_found:
                    booking_data['outbound_flight'] = extract_flight_segment_details(segment_text, 'outbound')
                    outbound_found = True
            elif any(keyword in segment_text.lower() for keyword in ['return', 'tue, aug 12', 'mco', 'orlando']):
                if not return_found:
                    booking_data['return_flight'] = extract_flight_segment_details(segment_text, 'return')
                    return_found = True
        
        # Extract baggage information
        baggage_info = []
        baggage_elements = soup.select('[data-testid*="bag"], .baggage-info, .bag-fee')
        for bag_elem in baggage_elements:
            bag_text = bag_elem.get_text(strip=True)
            if '$' in bag_text and ('bag' in bag_text.lower() or 'carry' in bag_text.lower()):
                baggage_info.append(bag_text)
        
        if baggage_info:
            booking_data['baggage_fees'] = baggage_info
    
    except Exception as e:
        print(f"Error extracting booking summary: {e}")
    
    return booking_data

def extract_flight_segment_details(text, direction):
    """
    Extract detailed flight information from a flight segment
    """
    import re
    
    segment_data = {
        'direction': direction,
        'raw_text': text
    }
    
    # Extract times
    times = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', text)
    if times:
        segment_data['departure_time'] = times[0] if len(times) > 0 else None
        segment_data['arrival_time'] = times[1] if len(times) > 1 else None
    
    # Extract duration
    duration_match = re.search(r'\d+\s*hr?\s*\d*\s*min?', text)
    if duration_match:
        segment_data['duration'] = duration_match.group()
    
    # Extract airline
    airline_patterns = ['Spirit', 'American', 'Delta', 'United', 'Southwest', 'JetBlue', 'Alaska', 'Frontier']
    for airline in airline_patterns:
        if airline.lower() in text.lower():
            segment_data['airline'] = airline
            break
    
    # Extract airport codes
    airport_codes = re.findall(r'\b[A-Z]{3}\b', text)
    if len(airport_codes) >= 2:
        segment_data['origin_airport'] = airport_codes[0]
        segment_data['destination_airport'] = airport_codes[1]
    
    # Extract stops
    if 'nonstop' in text.lower():
        segment_data['stops'] = 0
        segment_data['stop_type'] = 'Nonstop'
    elif '1 stop' in text.lower():
        segment_data['stops'] = 1
        segment_data['stop_type'] = '1 stop'
        # Extract layover details
        layover_match = re.search(r'(\d+\s*hr?\s*\d*\s*min?).*?([A-Z]{3})', text)
        if layover_match:
            segment_data['layover_duration'] = layover_match.group(1)
            segment_data['layover_airport'] = layover_match.group(2)
    
    # Extract CO2 emissions
    co2_match = re.search(r'(\d+)\s*kg\s*CO2e', text)
    if co2_match:
        segment_data['co2_emissions'] = f"{co2_match.group(1)} kg CO2e"
    
    return segment_data

def extract_detailed_flight_path(soup):
    """
    Extract detailed flight path information from expanded flight details
    """
    detailed_flights = []
    
    try:
        # Look for expanded flight detail sections with more comprehensive selectors
        detail_selectors = [
            '[data-testid*="flight-details"]',
            '[data-testid*="flight"][aria-expanded="true"]',
            '[role="region"][aria-expanded="true"]',
            '.flight-details',
            '.expanded-flight-info',
            'section[aria-expanded="true"]',
            '[jsaction*="flight"]',
            '.flight-segment-container',
            '.itinerary-details'
        ]
        
        detail_sections = []
        for selector in detail_selectors:
            sections = soup.select(selector)
            if sections:
                detail_sections.extend(sections)
                break
        
        # If no specific detail sections, look for flight segment information
        if not detail_sections:
            # Look for flight segments/legs with broader selectors
            segment_selectors = [
                '.flight-segment',
                '.flight-leg',
                '[data-testid*="segment"]',
                '[data-testid*="leg"]',
                '.itinerary-segment',
                '.segment-info',
                '.leg-info',
                '[role="listitem"]',
                'li[jsaction]',
                'div[jsaction*="flight"]'
            ]
            
            for selector in segment_selectors:
                segments = soup.select(selector)
                if segments:
                    detail_sections.extend(segments)
                    break
        
        for i, section in enumerate(detail_sections[:10]):  # Limit to first 10
            flight_detail = {
                'flight_index': i + 1,
                'segments': [],
                'total_duration': None,
                'layovers': [],
                'raw_html': str(section)[:500]  # First 500 chars for debugging
            }
            
            text_content = section.get_text(strip=True)
            
            # Extract flight numbers (e.g., "F9 1448", "UA 123")
            import re
            flight_numbers = re.findall(r'[A-Z]{1,3}\s*\d{3,4}', text_content)
            if flight_numbers:
                flight_detail['flight_numbers'] = flight_numbers
            
            # Extract airport codes (3-letter codes)
            airport_codes = re.findall(r'\b[A-Z]{3}\b', text_content)
            if airport_codes:
                flight_detail['airports'] = list(set(airport_codes))  # Remove duplicates
            
            # Extract times
            times = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', text_content)
            if times:
                flight_detail['times'] = times
            
            # Extract durations
            durations = re.findall(r'\d+h\s*\d*m?', text_content)
            if durations:
                flight_detail['durations'] = durations
                if durations:
                    flight_detail['total_duration'] = durations[0]  # First is usually total
            
            # Extract layover information
            layover_patterns = [
                r'(\d+\s*hr?\s*\d*\s*min?)\s*layover',
                r'layover[:\s]*(\d+\s*hr?\s*\d*\s*min?)',
                r'(\d+\s*hr?\s*\d*\s*min?)\s*in\s*([A-Z]{3})'
            ]
            
            for pattern in layover_patterns:
                layovers = re.findall(pattern, text_content, re.IGNORECASE)
                if layovers:
                    flight_detail['layovers'].extend(layovers)
            
            # Extract airline name
            airline_patterns = ['United', 'Delta', 'American', 'Southwest', 'JetBlue', 'Alaska', 'Spirit', 'Frontier', 'Hawaiian']
            for airline in airline_patterns:
                if airline.lower() in text_content.lower():
                    flight_detail['airline'] = airline
                    break
            
            # Extract price if visible
            price_match = re.search(r'\$[\d,]+', text_content)
            if price_match:
                flight_detail['price'] = price_match.group()
            
            # Try to parse individual segments
            segments = []
            
            # Look for segment patterns like "SFO → ATL" or "10:03 PM – 5:45 AM"
            segment_patterns = [
                r'([A-Z]{3})\s*[→–-]\s*([A-Z]{3})',  # Airport to airport
                r'(\d{1,2}:\d{2}\s*[AP]M)\s*[–-]\s*(\d{1,2}:\d{2}\s*[AP]M)'  # Time to time
            ]
            
            for pattern in segment_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    segments.append({
                        'from': match[0],
                        'to': match[1]
                    })
            
            if segments:
                flight_detail['segments'] = segments
            
            # Enhanced data validation and debugging
            has_meaningful_data = any([
                flight_detail.get('flight_numbers'),
                flight_detail.get('airports'),
                flight_detail.get('times'),
                flight_detail.get('segments'),
                flight_detail.get('airline'),
                flight_detail.get('price')
            ])
            
            if has_meaningful_data:
                detailed_flights.append(flight_detail)
            elif text_content and len(text_content) > 20:  # Has substantial text content
                # Add as raw data for debugging
                flight_detail['debug_text'] = text_content[:200]  # First 200 chars
                detailed_flights.append(flight_detail)
        
        print(f"✅ Extracted detailed path information for {len(detailed_flights)} flights")
        return detailed_flights
        
    except Exception as e:
        print(f"⚠️  Error extracting detailed flight paths: {e}")
        return []
    
    try:
        # Enhanced selectors for Google Flights data (2025 structure)
        flight_selectors = [
            '[data-testid*="flight"]',
            '[jsaction*="flight"]',
            '.pIav2d',  # Common Google Flights result class
            '[role="listitem"]',
            '.yR1fYc',  # Another common class
            '.Ir0Voe',  # Flight card container
            'li[data-ved]',  # Google search result items
            'div[data-ved]',  # Alternative result containers
            '.flight-result',
            '.result-item',
            '[data-testid*="offer"]',
            'div[jsaction][role="button"]'  # Clickable flight cards
        ]
        
        # Try to find flight elements
        flight_elements = []
        for selector in flight_selectors:
            elements = soup.select(selector)
            if elements:
                flight_elements.extend(elements)
                break
        
        # Enhanced debugging and fallback extraction
        if not flight_elements:
            print("🔍 No flight elements found with standard selectors, trying fallback methods...")
            
            # Look for elements containing price patterns
            price_elements = soup.find_all(text=lambda text: text and '$' in str(text))
            if price_elements:
                print(f"💰 Found {len(price_elements)} elements with price information")
                
                # Try to find parent containers of price elements
                for price_text in price_elements[:10]:  # Limit to first 10
                    parent = price_text.parent
                    if parent:
                        # Walk up the DOM to find meaningful containers
                        for _ in range(5):  # Go up max 5 levels
                            if parent and (parent.get('data-testid') or parent.get('jsaction') or parent.get('role')):
                                flight_elements.append(parent)
                                break
                            parent = parent.parent if parent else None
            
            # Also try to find elements with flight-related attributes
            flight_attrs = soup.find_all(attrs={'data-testid': True})
            flight_related = [elem for elem in flight_attrs if 'flight' in str(elem.get('data-testid', '')).lower()]
            if flight_related:
                print(f"✈️  Found {len(flight_related)} elements with flight-related data-testid")
                flight_elements.extend(flight_related[:10])
            
            # Try jsaction attributes
            jsaction_elements = soup.find_all(attrs={'jsaction': True})
            flight_jsaction = [elem for elem in jsaction_elements if 'flight' in str(elem.get('jsaction', '')).lower()]
            if flight_jsaction:
                print(f"🎯 Found {len(flight_jsaction)} elements with flight-related jsaction")
                flight_elements.extend(flight_jsaction[:10])
        
        # Extract data from flight elements
        for i, element in enumerate(flight_elements[:20]):  # Limit to first 20
            flight_info = {}
            
            # Extract text content
            text_content = element.get_text(strip=True)
            if text_content:
                flight_info['raw_text'] = text_content
                
                # Look for price patterns
                import re
                price_match = re.search(r'\$[\d,]+', text_content)
                if price_match:
                    flight_info['price'] = price_match.group()
                
                # Look for time patterns (e.g., "6:00 AM", "2:30 PM")
                time_matches = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', text_content)
                if time_matches:
                    flight_info['times'] = time_matches
                
                # Look for duration patterns (e.g., "5h 30m")
                duration_match = re.search(r'\d+h\s*\d*m?', text_content)
                if duration_match:
                    flight_info['duration'] = duration_match.group()
                
                # Look for airline names (common patterns)
                airline_patterns = [
                    'United', 'Delta', 'American', 'Southwest', 'JetBlue', 'Alaska', 
                    'Spirit', 'Frontier', 'Hawaiian', 'Allegiant', 'Sun Country',
                    'Breeze', 'Avelo', 'Air Canada', 'WestJet', 'Lufthansa', 'British Airways'
                ]
                for airline in airline_patterns:
                    if airline.lower() in text_content.lower():
                        flight_info['airline'] = airline
                        break
                
                # Also look for airline codes (2-3 letters)
                airline_code_match = re.search(r'\b[A-Z]{2,3}\s+\d{3,4}\b', text_content)
                if airline_code_match and not flight_info.get('airline'):
                    flight_info['airline_code'] = airline_code_match.group().split()[0]
            
            # Extract attributes
            if element.get('data-testid'):
                flight_info['data_testid'] = element.get('data-testid')
            
            # Enhanced validation for basic flight data
            has_flight_data = any([
                flight_info.get('price'),
                flight_info.get('times'),
                flight_info.get('duration'),
                flight_info.get('airline'),
                flight_info.get('airline_code')
            ])
            
            if has_flight_data:
                flights.append(flight_info)
            elif text_content and len(text_content) > 15:  # Has some meaningful content
                # Add minimal info for debugging
                flight_info['debug_text'] = text_content[:150]
                flights.append(flight_info)
        
        # If still no flights found, do a broader search
        if not flights:
            # Look for any elements containing flight-related keywords
            keywords = ['flight', 'airline', 'departure', 'arrival', 'nonstop', 'stop']
            for keyword in keywords:
                elements = soup.find_all(text=lambda text: text and keyword.lower() in str(text).lower())
                if elements:
                    print(f"Found {len(elements)} elements containing '{keyword}'")
            
            # Extract all text that looks like prices
            import re
            all_text = soup.get_text()
            prices = re.findall(r'\$[\d,]+', all_text)
            if prices:
                flights.append({
                    'type': 'price_extraction',
                    'prices_found': list(set(prices)),  # Remove duplicates
                    'total_prices': len(prices)
                })
        
    except Exception as e:
        print(f"❌ Error extracting flight data: {e}")
        import traceback
        print(f"📍 Traceback: {traceback.format_exc()[:200]}...")  # First 200 chars of traceback
        return [{'error': str(e)}]
    
    return flights

async def search_and_continue():
    """
    Navigate to Google Flights, set up search, click search, and handle next steps
    """
    async with async_playwright() as p:
        # Launch browser (non-headless so we can see what's happening)
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🛫 Starting Google Flights automation...")
            print("-" * 50)
            
            # Step 1: Navigate to Google Flights
            print("Step 1: Navigating to Google Flights...")
            await page.goto("https://www.google.com/travel/flights")
            await page.wait_for_load_state('networkidle')
            
            # Step 2: Set origin to Louisville
            print("Step 2: Setting origin to Louisville...")
            
            # Click on the origin field ("Where from?")
            origin_field = page.get_by_role('combobox', name='Where from?')
            await origin_field.click()
            await page.wait_for_timeout(random.randint(150, 250))
            print("✅ Origin field clicked, dialog opened")
            
            # Wait for the origin dialog to appear and find the search combobox
            try:
                # The dialog contains a combobox with "Where else?" label
                origin_search = page.get_by_role('combobox', name='Where else?')
                await origin_search.fill('Louisville')
                await page.wait_for_timeout(random.randint(150, 250))
                print("✅ Typed 'Louisville' in origin search")
                
                # Select Louisville, Kentucky from the dropdown
                await page.get_by_role('option', name='Louisville, Kentucky').click()
                await page.wait_for_timeout(random.randint(150, 250))
                print("✅ Louisville, Kentucky selected as origin")
                
            except Exception as e:
                print(f"⚠️  Error setting origin: {e}")
                # Fallback: try pressing Enter
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(random.randint(150, 250))
            
            # Step 3: Set destination to Orlando
            print("Step 3: Setting destination to Orlando...")
            
            # Click on the destination field ("Where to?")
            dest_field = page.get_by_role('combobox', name='Where to?')
            await dest_field.click()
            await page.wait_for_timeout(random.randint(150, 250))
            print("✅ Destination field clicked, dialog opened")
            
            # Wait for the destination dialog to appear and find the search combobox
            try:
                # The dialog contains a combobox with "Where to?" label
                dest_search = page.get_by_role('combobox', name='Where to?')
                await dest_search.fill('Orlando')
                await page.wait_for_timeout(random.randint(150, 250))
                print("✅ Typed 'Orlando' in destination search")
                
                # Select Orlando from the dropdown (try different variations)
                orlando_options = [
                    'Orlando, Florida',
                    'Orlando',
                    'Orlando International Airport (MCO)'
                ]
                
                orlando_selected = False
                for option_name in orlando_options:
                    try:
                        await page.get_by_role('option', name=option_name).click()
                        await page.wait_for_timeout(random.randint(150, 250))
                        print(f"✅ {option_name} selected as destination")
                        orlando_selected = True
                        break
                    except:
                        continue
                
                if not orlando_selected:
                    print("⚠️  Trying Enter key for Orlando selection...")
                    await page.keyboard.press('Enter')
                    await page.wait_for_timeout(random.randint(150, 250))
                
            except Exception as e:
                print(f"⚠️  Error setting destination: {e}")
                # Fallback: try pressing Enter
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(random.randint(150, 250))
            
            # Step 4: Set departure date
            print("Step 4: Setting departure date to Aug 10, 2025...")
            departure_field = page.get_by_role('textbox', name='Departure')
            await departure_field.click()
            await page.wait_for_timeout(random.randint(150, 250))
            await departure_field.fill('Aug 10, 2025')
            await page.wait_for_timeout(random.randint(150, 250))
            
            # Step 5: Set return date
            print("Step 5: Setting return date to Aug 12, 2025...")
            return_field = page.get_by_role('textbox', name='Return')
            await return_field.click()
            await page.wait_for_timeout(random.randint(150, 250))
            await return_field.fill('Aug 12, 2025')
            await page.wait_for_timeout(random.randint(150, 250))
            
            # Step 5.5: Close date picker with double Enter (optimized)
            print("Step 5.5: Closing date picker with double Enter...")
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(random.randint(150, 250))
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(random.randint(150, 250))
            print("✅ Double Enter pressed to close date picker")
            
            # Step 5.6: Wait for date picker to close and verify search button is available
            print("Step 5.6: Waiting for date picker to close...")
            try:
                # Wait for any date picker dialog to disappear
                await page.wait_for_selector('dialog', state='detached', timeout=5000)
                print("✅ Date picker dialog closed")
            except Exception as e:
                print(f"⚠️  Date picker dialog still present or timeout: {e}")
            
            # Additional wait to ensure UI is ready
            await page.wait_for_timeout(random.randint(150, 250))
            
            # Step 6: Click Search button with multiple strategies
            print("Step 6: Clicking Search button...")
            try:
                # Strategy 1: Try the main search button
                search_button = page.get_by_role('button', name='Search')
                await search_button.click()
                print("✅ Search button clicked!")
            except Exception as e:
                print(f"⚠️  First search button strategy failed: {e}")
                try:
                    # Strategy 2: Try alternative search button selector
                    search_button = page.locator('button:has-text("Search")')
                    await search_button.click()
                    print("✅ Search button clicked with alternative selector!")
                except Exception as e2:
                    print(f"⚠️  Second search button strategy failed: {e2}")
                    try:
                        # Strategy 3: Press Enter to trigger search
                        print("Trying Enter key to trigger search...")
                        await page.keyboard.press('Enter')
                        await page.wait_for_timeout(random.randint(150, 250))
                        print("✅ Enter key pressed to trigger search!")
                    except Exception as e3:
                        print(f"⚠️  Enter key strategy failed: {e3}")
                        try:
                            # Strategy 4: Try explore button as fallback
                            explore_button = page.get_by_role('button', name='Explore')
                            await explore_button.click()
                            print("✅ Explore button clicked as fallback!")
                        except Exception as e4:
                            print(f"❌ All search strategies failed: {e4}")
                            raise e4
            
            # Step 7: Wait for results page to load and verify search worked
            print("Step 7: Waiting for search results to load...")
            try:
                # Wait for URL to change to search results page
                await page.wait_for_url('**/search?**', timeout=10000)
                print("✅ Successfully navigated to search results page")
            except Exception as e:
                print(f"⚠️  URL didn't change to search results: {e}")
                print(f"Current URL: {page.url}")
            
            # Wait for search results to appear
            try:
                await page.wait_for_selector('text="Search results"', timeout=10000)
                print("✅ Search results section found")
            except Exception as e:
                print(f"⚠️  Search results section not found: {e}")
            
            # Step 8: Wait for results to load
            print("Step 8: Waiting for flight results to load...")
            await page.wait_for_timeout(3000)  # Give more time for results to load
            
            # Check current URL and page title
            current_url = page.url
            page_title = await page.title()
            print(f"🔗 Current URL: {current_url}")
            
            # Step 9: Extract flight data from HTML
            print("Step 9: Extracting flight data from HTML...")
            
            try:
                # Wait a bit more for results to fully load
                await page.wait_for_timeout(2000)
                
                # Get the page HTML content
                page_content = await page.content()
                
                # Parse with BeautifulSoup for easier data extraction
                soup = BeautifulSoup(page_content, 'html.parser')
                
                # Extract flight information
                flight_data = extract_flight_data(soup)
                
                if flight_data:
                    print(f"✅ Extracted {len(flight_data)} flights from HTML")
                    if flight_data:
                        print("\n📊 Flight Data Summary:")
                        for i, flight in enumerate(flight_data[:5], 1):  # Show first 5 flights
                            print(f"  {i}. {flight}")
                    
                    # Save all data to JSON file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_file = f'flight_data_{timestamp}.json'
                    with open(json_file, 'w') as f:
                        json.dump(flight_data, f, indent=2)
                    print(f"💾 All flight data saved to '{json_file}'")
                else:
                    print("⚠️  No flight data found - may need to adjust selectors")
                    
            except Exception as e:
                print(f"⚠️  Error extracting flight data: {e}")
            
            # Step 10: Look for "Next" or pagination buttons and extract more data
            print("Step 10: Looking for Next/More results options...")
            
            try:
                # Common selectors for next/more buttons
                next_selectors = [
                    'button:has-text("Next")',
                    'button:has-text("More")',
                    'button:has-text("Show more")',
                    '[aria-label*="Next"]',
                    '[aria-label*="More"]'
                ]
                
                next_button_found = False
                for selector in next_selectors:
                    try:
                        next_button = await page.wait_for_selector(selector, timeout=2000)
                        if next_button:
                            print(f"✅ Found Next/More button with selector: {selector}")
                            
                            # Click the next button
                            await next_button.click()
                            print("🔄 Clicked Next/More button!")
                            
                            # Wait for new content to load
                            await page.wait_for_timeout(3000)
                            
                            # Extract additional flight data
                            additional_content = await page.content()
                            additional_soup = BeautifulSoup(additional_content, 'html.parser')
                            additional_flights = extract_flight_data(additional_soup)
                            
                            if additional_flights:
                                print(f"✅ Found {len(additional_flights)} additional flight options")
                                # Update the JSON file with additional data
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                json_file = f'additional_flight_data_{timestamp}.json'
                                with open(json_file, 'w') as f:
                                    json.dump(additional_flights, f, indent=2)
                                print(f"💾 Additional flight data saved to '{json_file}'")
                            
                            next_button_found = True
                            break
                    except:
                        continue
                
                if not next_button_found:
                    print("ℹ️  No Next/More buttons found - may be showing all results")
                    
            except Exception as e:
                print(f"⚠️  Error looking for Next button: {e}")
            
            # Step 11: Click on flight details to get complete path information
            print("Step 11: Clicking flight details to get complete path information...")
            
            flight_details_clicked = 0
            max_details_to_click = 5  # Focus on first 5 flights as requested
            
            try:
                # Look for "Flight details" buttons
                detail_button_selectors = [
                    'button[aria-label*="Flight details"]',
                    'button:has-text("Flight details")',
                    '[data-testid*="flight-details-button"]',
                    'button[title*="details"]',
                    '.flight-details-button'
                ]
                
                for selector in detail_button_selectors:
                    try:
                        detail_buttons = await page.query_selector_all(selector)
                        if detail_buttons:
                            print(f"Found {len(detail_buttons)} flight detail buttons with selector: {selector}")
                            
                            print(f"📋 Processing first {max_details_to_click} flight details as requested...")
                            for i, button in enumerate(detail_buttons[:max_details_to_click]):
                                try:
                                    # Check if button is visible and clickable
                                    is_visible = await button.is_visible()
                                    if is_visible:
                                        print(f"Clicking flight details button {i+1}...")
                                        await button.click()
                                        await page.wait_for_timeout(1500)  # Wait for details to expand
                                        flight_details_clicked += 1
                                        
                                        # Extract the expanded details immediately
                                        expanded_content = await page.content()
                                        expanded_soup = BeautifulSoup(expanded_content, 'html.parser')
                                        
                                        # Save the HTML for debugging
                                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                        html_debug_file = f'flight_detail_html_{i+1}_{timestamp}.html'
                                        with open(html_debug_file, 'w', encoding='utf-8') as f:
                                            f.write(expanded_content)
                                        print(f"🔍 HTML saved for debugging: '{html_debug_file}'")
                                        
                                        # Try to extract flight path data with enhanced methods
                                        detailed_paths = extract_detailed_flight_path(expanded_soup)
                                        
                                        # Also try to extract any visible text that might contain flight info
                                        flight_text_data = []
                                        
                                        # Look for text containing flight numbers, airports, times
                                        import re
                                        all_text = expanded_soup.get_text()
                                        
                                        # Extract flight numbers (like "F9 1448", "UA 123")
                                        flight_numbers = re.findall(r'[A-Z]{1,3}\s+\d{3,4}', all_text)
                                        if flight_numbers:
                                            flight_text_data.append({"flight_numbers": flight_numbers})
                                        
                                        # Extract airport codes
                                        airport_codes = re.findall(r'\b[A-Z]{3}\b', all_text)
                                        if airport_codes:
                                            # Filter to likely airport codes (common ones)
                                            likely_airports = [code for code in airport_codes if code in [
                                                'SDF', 'MCO', 'ATL', 'DFW', 'ORD', 'LAX', 'JFK', 'LGA', 'EWR', 'SFO', 'SEA', 'DEN', 'PHX', 'LAS', 'MIA', 'BOS', 'IAD', 'BWI', 'PHL', 'CLT', 'MSP', 'DTW', 'IAH', 'MDW', 'FLL', 'TPA', 'SAN', 'STL', 'HNL'
                                            ]]
                                            if likely_airports:
                                                flight_text_data.append({"airports": likely_airports})
                                        
                                        # Extract times
                                        times = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', all_text)
                                        if times:
                                            flight_text_data.append({"times": times})
                                        
                                        # Extract durations
                                        durations = re.findall(r'\d+h\s*\d*m?|\d+\s*hr\s*\d*\s*min', all_text)
                                        if durations:
                                            flight_text_data.append({"durations": durations})
                                        
                                        # Combine all extracted data
                                        combined_data = {
                                            'flight_index': i + 1,
                                            'detailed_paths': detailed_paths,
                                            'text_extracted_data': flight_text_data,
                                            'html_debug_file': html_debug_file
                                        }
                                        
                                        # Save individual flight detail
                                        detail_file = f'flight_detail_{i+1}_{timestamp}.json'
                                        with open(detail_file, 'w') as f:
                                            json.dump(combined_data, f, indent=2)
                                        print(f"💾 Flight {i+1} data saved to '{detail_file}'")
                                        
                                        if detailed_paths or flight_text_data:
                                            print(f"✅ Extracted data for flight {i+1}: {len(detailed_paths)} detailed paths, {len(flight_text_data)} text extractions")
                                        else:
                                            print(f"⚠️  No flight path data extracted for flight {i+1}")
                                        
                                        # Click again to collapse (optional)
                                        try:
                                            await button.click()
                                            await page.wait_for_timeout(500)
                                        except:
                                            pass  # Ignore if collapse fails
                                        
                                except Exception as e:
                                    print(f"⚠️  Error clicking detail button {i+1}: {e}")
                                    continue
                            break  # Found working selector, stop trying others
                    except Exception as e:
                        print(f"⚠️  Error with selector {selector}: {e}")
                        continue
                
                if flight_details_clicked > 0:
                    print(f"✅ Successfully clicked {flight_details_clicked} flight detail buttons")
                else:
                    print("ℹ️  No flight detail buttons found or clickable")
                    
            except Exception as e:
                print(f"⚠️  Error clicking flight details: {e}")
            
            # Step 12: Final comprehensive data extraction
            print("Step 12: Final comprehensive data extraction...")
            await page.wait_for_timeout(2000)
            
            # Final comprehensive data extraction
            final_content = await page.content()
            final_soup = BeautifulSoup(final_content, 'html.parser')
            final_flight_data = extract_flight_data(final_soup)
            
            # Also extract any remaining detailed path information
            final_detailed_paths = extract_detailed_flight_path(final_soup)
            
            # Get current URL to see where we ended up
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            # Step 12: Start comprehensive round trip workflow
            print("\n🎯 Starting comprehensive round trip workflow...")
            combinations = await comprehensive_round_trip_workflow(page, max_outbound=3, max_return=2)
            
            # Save comprehensive results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f'comprehensive_round_trip_results_{timestamp}.json'
            
            results = {
                'timestamp': timestamp,
                'search_details': {
                    'route': 'Louisville (SDF) ↔ Orlando (MCO)',
                    'dates': 'August 10-12, 2025'
                },
                'total_combinations': len(combinations),
                'combinations': combinations,
                'basic_flights': final_flight_data if final_flight_data else [],
                'detailed_paths': final_detailed_paths if final_detailed_paths else []
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {results_file}")
            
            # Display comprehensive results
            search_details = {
                'route': 'Louisville (SDF) ↔ Orlando (MCO)',
                'dates': 'August 10-12, 2025'
            }
            display_comprehensive_results(combinations, search_details)
            
            print(f"\n📊 Summary:")
            print(f"   • Basic flights found: {len(final_flight_data) if final_flight_data else 0}")
            print(f"   • Round trip combinations: {len(combinations)}")
            print(f"   • Flight details clicked: {flight_details_clicked}")
            
            print("\n✅ Comprehensive round trip search completed successfully!")
            
            # Keep browser open for manual inspection
            print("\n⏳ Keeping browser open for 10 seconds for manual inspection...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            # Save error page HTML for debugging
            error_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                error_content = await page.content()
                error_file = f'error_page_{error_timestamp}.html'
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(error_content)
                print(f"💾 Error page HTML saved as '{error_file}'")
            except:
                print("Could not save error page HTML")
            raise e
            
        finally:
            await browser.close()

async def enhanced_sequential_workflow(page, max_outbound=3, max_return=3):
    """
    Enhanced sequential round trip workflow with robust testing patterns
    Processes one outbound-return combination at a time using proven navigation patterns
    
    Flow: Outbound 1 → Select → Return 1 → Go back twice → Outbound 2 → Select → Return 1 → Go back twice...
    
    Enhanced Features:
    - Robust element detection and clicking strategies
    - Improved error handling and recovery
    - Better page state validation
    - Enhanced data extraction with BeautifulSoup
    - Adaptive retry mechanisms
    
    Args:
        page: Playwright page object
        max_outbound: Maximum number of outbound flights to test (default 3)
        max_return: Maximum number of return flights to test per outbound (default 3)
    """
    all_combinations = []
    
    try:
        print("\n🎯 Starting sequential round trip workflow...")
        
        # Wait for flight results to load
        await page.wait_for_timeout(5000)
        
        # Extract initial outbound flights once
        print("📋 Extracting outbound flight options...")
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        outbound_flights = extract_flight_options(soup)
        
        print(f"✅ Found {len(outbound_flights)} outbound flights")
        
        # Process flights sequentially: each outbound with each return, one at a time
        max_outbound = min(max_outbound, len(outbound_flights))
        
        # Create all combinations to process sequentially
        combinations_to_process = []
        for outbound_idx in range(max_outbound):
            for return_idx in range(max_return):
                combinations_to_process.append((outbound_idx, return_idx))
        
        print(f"🔄 Will process {len(combinations_to_process)} combinations sequentially")
        
        # Track failed attempts for adaptive strategy
        failed_attempts = 0
        max_failures = 3
        
        for combo_num, (outbound_idx, return_idx) in enumerate(combinations_to_process):
            print(f"\n{'='*60}")
            print(f"🎯 COMBINATION {combo_num + 1}/{len(combinations_to_process)}")
            print(f"   Outbound Flight #{outbound_idx + 1} → Return Flight #{return_idx + 1}")
            print(f"{'='*60}")
            
            try:
                # Navigate back to main search results if not first combination
                if combo_num > 0:
                    print("🔙 Navigating back to main search results...")
                    await page.go_back()
                    await page.wait_for_timeout(1000)
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                    
                    # Close any overlays or popups that might interfere
                    try:
                        # Try to close any modal dialogs
                        close_buttons = await page.locator('[aria-label*="Close"], [aria-label*="close"], button:has-text("×")').all()
                        for close_btn in close_buttons[:3]:  # Limit to first 3
                            try:
                                await close_btn.click(timeout=1000)
                                await page.wait_for_timeout(500)
                            except:
                                pass
                    except:
                        pass
                    
                    # Press Escape to close any remaining overlays
                    try:
                        await page.keyboard.press('Escape')
                        await page.wait_for_timeout(500)
                    except:
                        pass
                    
                    print("✅ Back to main search results")
                
                # Step 1: Click outbound flight with enhanced strategies
                outbound_flight = outbound_flights[outbound_idx] if outbound_idx < len(outbound_flights) else {}
                print(f"\n🛫 STEP 1: Clicking Outbound Flight #{outbound_idx + 1}")
                print(f"   {outbound_flight.get('airline', 'Unknown')} - {outbound_flight.get('price', 'N/A')}")
                print(f"   {outbound_flight.get('departure_time', 'N/A')} → {outbound_flight.get('arrival_time', 'N/A')}")
                
                clicked_outbound = False
                # Enhanced clicking strategies based on successful patterns
                strategies = [
                    ('.gQ6yfe', 'Main flight container'),
                    ('[role="listitem"]', 'List item'),
                    ('[data-testid*="flight"]', 'Flight test ID'),
                    ('.pIav2d', 'Flight item'),
                    ('.yR1fYc', 'Flight row'),
                    ('li[jsaction*="click"]', 'Clickable list item'),
                    ('div[jsaction*="click"]', 'Clickable div'),
                    ('button[aria-label*="Select"]', 'Select button'),
                    ('a[href*="booking"]', 'Booking link')
                ]
                
                for selector, desc in strategies:
                    try:
                        elements = await page.locator(selector).all()
                        if len(elements) > outbound_idx:
                            element = elements[outbound_idx]
                            
                            # Enhanced clicking methods with better error handling
                            click_methods = [
                                ('force_click', lambda: element.click(force=True)),
                                ('scroll_and_click', lambda: self._scroll_and_click(element)),
                                ('js_click', lambda: element.evaluate('el => el.click()')),
                                ('hover_and_click', lambda: self._hover_and_click(element)),
                                ('double_click', lambda: element.dblclick(force=True))
                            ]
                            
                            for method_name, click_func in click_methods:
                                try:
                                    if method_name == 'scroll_and_click':
                                        await element.scroll_into_view_if_needed()
                                        await page.wait_for_timeout(500)
                                        await element.click()
                                    elif method_name == 'hover_and_click':
                                        await element.hover()
                                        await page.wait_for_timeout(300)
                                        await element.click()
                                    else:
                                        await click_func()
                                    
                                    # Verify click was successful by checking page state
                                    await page.wait_for_timeout(1000)
                                    current_url = page.url
                                    if 'booking' in current_url or await page.locator('[data-testid*="return"], .return-flight').first.is_visible():
                                        clicked_outbound = True
                                        print(f"✅ Outbound flight clicked using {desc} ({method_name})")
                                        break
                                except Exception as method_error:
                                    print(f"   ⚠️  {method_name} failed: {method_error}")
                                    continue
                            
                            if clicked_outbound:
                                break
                                
                    except Exception as e:
                        print(f"   ⚠️  {desc} strategy failed: {e}")
                        continue
                
                if not clicked_outbound:
                    print(f"❌ Could not click outbound flight #{outbound_idx + 1}")
                    failed_attempts += 1
                    if failed_attempts >= max_failures:
                        print(f"⚠️  Too many failures ({failed_attempts}), reducing combinations...")
                        # Try only first flight combinations to ensure some success
                        if outbound_idx > 0 or return_idx > 0:
                            print("🔄 Switching to first flight only strategy")
                            combinations_to_process = [(0, 0)]  # Just try first combination
                    continue
                
                # Wait for return flight page to load
                await page.wait_for_timeout(5000)
                print("✅ Waiting for return flight page...")
                
                # Step 2: Extract return flight options from current page
                print(f"\n🛬 STEP 2: Extracting return flight options...")
                
                # Wait for return flights to load and verify page state
                retry_count = 0
                max_retries = 3
                return_flights = []
                
                while retry_count < max_retries and len(return_flights) == 0:
                    await page.wait_for_timeout(2000)  # Give more time for loading
                    return_content = await page.content()
                    return_soup = BeautifulSoup(return_content, 'html.parser')
                    return_flights = extract_flight_options(return_soup)
                    
                    if len(return_flights) == 0:
                        print(f"⚠️  No return flights found, retry {retry_count + 1}/{max_retries}")
                        retry_count += 1
                        # Try refreshing the page or clicking again if no flights found
                        if retry_count < max_retries:
                            await page.reload()
                            await page.wait_for_timeout(3000)
                    else:
                        break
                
                print(f"✅ Found {len(return_flights)} return flights on this page")
                
                # Step 3: Click on the specific return flight
                if return_idx < len(return_flights):
                    return_flight = return_flights[return_idx]
                    print(f"\n🎯 STEP 3: Clicking Return Flight #{return_idx + 1}")
                    print(f"   {return_flight.get('airline', 'Unknown')} - {return_flight.get('price', 'N/A')}")
                    print(f"   {return_flight.get('departure_time', 'N/A')} → {return_flight.get('arrival_time', 'N/A')}")
                    
                    clicked_return = False
                    for selector, desc in strategies:
                        try:
                            elements = await page.locator(selector).all()
                            if len(elements) > return_idx:
                                # Try multiple click methods to avoid interception
                                element = elements[return_idx]
                                
                                # Method 1: Force click (ignores intercepting elements)
                                try:
                                    await element.click(force=True)
                                    clicked_return = True
                                    print(f"✅ Return flight clicked using {desc} (force)")
                                    break
                                except:
                                    pass
                                
                                # Method 2: Scroll into view then click
                                try:
                                    await element.scroll_into_view_if_needed()
                                    await page.wait_for_timeout(500)
                                    await element.click()
                                    clicked_return = True
                                    print(f"✅ Return flight clicked using {desc} (scroll)")
                                    break
                                except:
                                    pass
                                
                                # Method 3: JavaScript click
                                try:
                                    await element.evaluate('el => el.click()')
                                    clicked_return = True
                                    print(f"✅ Return flight clicked using {desc} (JS)")
                                    break
                                except:
                                    pass
                                    
                        except Exception as e:
                            print(f"   ⚠️  {desc} failed: {e}")
                            continue
                    
                    if not clicked_return:
                        print(f"❌ Could not click return flight #{return_idx + 1}")
                        continue
                    
                    # Wait for booking/summary page
                    await page.wait_for_timeout(5000)
                    print("✅ Waiting for booking page...")
                    
                    # Step 4: Extract round-trip total using double-back pattern
                    print(f"\n💰 STEP 4: Extracting round-trip total (Double-back pattern)")
                    
                    # Go back once
                    print("🔙 Going back (1st time)...")
                    await page.go_back()
                    await page.wait_for_timeout(1000)
                    
                    # Go back again
                    print("🔙 Going back (2nd time)...")
                    await page.go_back()
                    await page.wait_for_timeout(2000)
                    
                    # Extract the round-trip total from this page
                    total_content = await page.content()
                    total_soup = BeautifulSoup(total_content, 'html.parser')
                    round_trip_total = extract_round_trip_total_after_back(total_soup)
                    
                    # Store combination data
                    combination_data = {
                        'combination_number': combo_num + 1,
                        'outbound_index': outbound_idx + 1,
                        'return_index': return_idx + 1,
                        'outbound_flight': outbound_flight,
                        'return_flight': return_flight,
                        'round_trip_total': round_trip_total,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    all_combinations.append(combination_data)
                    
                    print(f"✅ COMBINATION COMPLETE!")
                    print(f"   💰 Round-trip total: {round_trip_total}")
                    print(f"   🛫 Outbound: {outbound_flight.get('airline', 'Unknown')} {outbound_flight.get('price', 'N/A')}")
                    print(f"   🛬 Return: {return_flight.get('airline', 'Unknown')} {return_flight.get('price', 'N/A')}")
                    
                else:
                    print(f"⚠️  Return flight #{return_idx + 1} not available (only {len(return_flights)} found)")
                    continue
                    
            except Exception as e:
                print(f"❌ Error processing combination {combo_num + 1}: {e}")
                continue
        
        # Save results to JSON file
        if all_combinations:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f'sequential_round_trip_results_{timestamp}.json'
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'search_timestamp': timestamp,
                    'total_combinations': len(all_combinations),
                    'combinations': all_combinations
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {results_file}")
            
            # Display summary
            display_comprehensive_results(all_combinations)
        else:
            print("⚠️  No combinations were successfully processed")
            
    except Exception as e:
        print(f"❌ Error in sequential workflow: {e}")
        
    return all_combinations

def display_comprehensive_results(combinations, search_details=None):
    """
    Display comprehensive round trip results in a user-friendly format
    """
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE ROUND TRIP RESULTS")
    print("="*80)
    
    if search_details:
        print(f"📍 Route: {search_details.get('route', 'N/A')}")
        print(f"📅 Dates: {search_details.get('dates', 'N/A')}")
        print()
    
    print(f"📊 Total combinations found: {len(combinations)}")
    print()
    
    if combinations:
        # Sort by total price
        sorted_combinations = sorted(combinations, key=lambda x: 
            int(x['total_price'].replace('$', '').replace(',', '')) if x['total_price'] and x['total_price'] != 'N/A' else 999999)
        
        print("💰 BEST ROUND TRIP DEALS (sorted by price)")
        print("-" * 60)
        
        for i, combo in enumerate(sorted_combinations, 1):
            outbound = combo['outbound_flight']
            return_flight = combo['return_flight']
            
            print(f"{i}. COMBINATION {combo['combination_id']} - {combo['total_price']}")
            print(f"   🛫 Outbound: {outbound['airline']} {outbound['departure_time']}→{outbound['arrival_time']} ({outbound['stops']})")
            print(f"   🛬 Return: {return_flight['airline']} {return_flight['departure_time']}→{return_flight['arrival_time']} ({return_flight['stops']})")
            print()
        
        # Show cheapest option
        cheapest = sorted_combinations[0]
        print("🏆 BEST DEAL SUMMARY")
        print("-" * 30)
        print(f"💰 Cheapest Total: {cheapest['total_price']}")
        print(f"🛫 Outbound: {cheapest['outbound_flight']['airline']} ({cheapest['outbound_flight']['stops']})")
        print(f"🛬 Return: {cheapest['return_flight']['airline']} ({cheapest['return_flight']['stops']})")
    else:
        print("❌ No combinations found")
    
    print("\n" + "="*80)

async def handle_select_button_workflow(page):
    """
    Legacy function - now calls comprehensive workflow
    """
    workflow_data = {
        'outbound_flights': [],
        'return_flights': [],
        'selected_outbound': {},
        'selected_return': {},
        'booking_summary': {},
        'workflow_completed': False
    }
    
    try:
        print("\n🎯 Starting Select button workflow...")
        
        # Wait for flight results to load
        await page.wait_for_timeout(3000)
        
        # Step 1: FIRST extract outbound flight options from current page
        print("📋 Step 1: Extracting outbound flight options from current page...")
        current_content = await page.content()
        soup = BeautifulSoup(current_content, 'html.parser')
        outbound_flights = extract_flight_data(soup)
        workflow_data['outbound_flights'] = outbound_flights if outbound_flights else []
        print(f"✅ Found {len(workflow_data['outbound_flights'])} outbound flights")
        
        # Save outbound page HTML for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outbound_html_file = f'outbound_flights_page_{timestamp}.html'
        with open(outbound_html_file, 'w', encoding='utf-8') as f:
            f.write(current_content)
        print(f"💾 Outbound flights page saved as '{outbound_html_file}'")
        
        # Step 2: FIRST click Select on first available flight (priority: click first!)
        print("🖱️  Step 2: FIRST clicking Select on first outbound flight...")
        
        # Look for flight links with "Select flight" text - try multiple strategies
        select_strategies = [
            ('.gQ6yfe', 'Main flight container link'),
            ('a[href*="booking"]', 'Booking link'),
            ('[role="link"]', 'Role link'),
            ('a[aria-label*="Select"]', 'Select aria-label'),
            ('[data-testid*="flight"] a', 'Flight testid link'),
            ('button:has-text("Select")', 'Select button'),
            ('a:has-text("Select flight")', 'Select flight link')
        ]
        
        clicked_outbound = False
        for selector, description in select_strategies:
            try:
                print(f"   Trying: {description} ({selector})")
                # Click the first flight option
                await page.locator(selector).first.click()
                clicked_outbound = True
                print(f"✅ Successfully clicked outbound flight using: {description}")
                break
            except Exception as e:
                print(f"   ⚠️  {description} failed: {e}")
                continue
        
        if not clicked_outbound:
            print("❌ Could not click any outbound flight - trying fallback approach")
            # Fallback: try clicking any clickable element in flight results
            try:
                await page.locator('li').first.click()
                clicked_outbound = True
                print("✅ Fallback click succeeded")
            except Exception as e:
                print(f"❌ Fallback also failed: {e}")
                return workflow_data
        
        # Wait for return flight page to load
        await page.wait_for_timeout(5000)
        
        # Step 3: Check if we're on return flight selection page
        current_url = page.url
        page_title = await page.title()
        print(f"📍 Step 3: Current page: {page_title}")
        print(f"🔗 URL: {current_url}")
        
        if "orlando to louisville" in page_title.lower() or "return" in current_url.lower():
            print("✅ Successfully reached return flight selection page")
            
            # Step 3a: THEN extract return flight options
            print("📋 Step 3a: THEN extracting return flight options...")
            return_content = await page.content()
            return_soup = BeautifulSoup(return_content, 'html.parser')
            return_flights = extract_return_flight_data(return_soup)
            workflow_data['return_flights'] = return_flights if return_flights else []
            print(f"✅ Found {len(workflow_data['return_flights'])} return flights")
            
            # Save return flight page HTML for debugging
            return_html_file = f'return_flights_page_{timestamp}.html'
            with open(return_html_file, 'w', encoding='utf-8') as f:
                f.write(return_content)
            print(f"💾 Return flights page saved as '{return_html_file}'")
            
            # Step 4: FIRST click Select on first return flight (priority: click first!)
            print("🖱️  Step 4: FIRST clicking Select on first return flight...")
            
            clicked_return = False
            for selector, description in select_strategies:
                try:
                    print(f"   Trying return: {description} ({selector})")
                    await page.locator(selector).first.click()
                    clicked_return = True
                    print(f"✅ Successfully clicked return flight using: {description}")
                    break
                except Exception as e:
                    print(f"   ⚠️  Return {description} failed: {e}")
                    continue
            
            if clicked_return:
                # Wait for booking summary page
                await page.wait_for_timeout(5000)
                
                # Step 5: Check final page and THEN extract complete booking summary
                final_url = page.url
                final_title = await page.title()
                print(f"📍 Step 5: Final page: {final_title}")
                print(f"🔗 Final URL: {final_url}")
                
                if "booking" in final_url.lower() or "round trip" in final_title.lower():
                    print("✅ Successfully reached booking summary page")
                    
                    # Step 5a: THEN extract complete booking summary
                    print("📋 Step 5a: THEN extracting complete booking summary...")
                    booking_content = await page.content()
                    booking_soup = BeautifulSoup(booking_content, 'html.parser')
                    booking_summary = extract_booking_summary_data(booking_soup)
                    workflow_data['booking_summary'] = booking_summary if booking_summary else {}
                    
                    # Save booking summary HTML
                    booking_html_file = f'booking_summary_{timestamp}.html'
                    with open(booking_html_file, 'w', encoding='utf-8') as f:
                        f.write(booking_content)
                    print(f"💾 Booking summary saved as '{booking_html_file}'")
                    
                    workflow_data['workflow_completed'] = True
                    print("🎉 Complete Select button workflow finished successfully!")
                    
                    # Extract selected flight details from booking summary
                    if booking_summary and booking_summary.get('outbound_flight'):
                        workflow_data['selected_outbound'] = booking_summary['outbound_flight']
                    if booking_summary and booking_summary.get('return_flight'):
                        workflow_data['selected_return'] = booking_summary['return_flight']
                    
                    total_price = booking_summary.get('total_price', 'N/A') if booking_summary else 'N/A'
                    outbound_airline = booking_summary.get('outbound_flight', {}).get('airline', 'N/A') if booking_summary else 'N/A'
                    return_airline = booking_summary.get('return_flight', {}).get('airline', 'N/A') if booking_summary else 'N/A'
                    
                    print(f"💰 Total price: {total_price}")
                    print(f"✈️  Outbound: {outbound_airline}")
                    print(f"🔄 Return: {return_airline}")
                else:
                    print("⚠️  Did not reach expected booking summary page")
                    print("📋 Extracting data from current page anyway...")
                    # Still try to extract data from whatever page we're on
                    booking_content = await page.content()
                    booking_soup = BeautifulSoup(booking_content, 'html.parser')
                    booking_summary = extract_booking_summary_data(booking_soup)
                    workflow_data['booking_summary'] = booking_summary if booking_summary else {}
            else:
                print("❌ Could not click return flight - trying fallback approach")
                # Fallback: try clicking any clickable element
                try:
                    await page.locator('li').first.click()
                    print("✅ Fallback return click succeeded")
                    await page.wait_for_timeout(3000)
                    # Extract data from whatever page we end up on
                    final_content = await page.content()
                    final_soup = BeautifulSoup(final_content, 'html.parser')
                    booking_summary = extract_booking_summary_data(final_soup)
                    workflow_data['booking_summary'] = booking_summary if booking_summary else {}
                except Exception as e:
                    print(f"❌ Fallback return click also failed: {e}")
        else:
            print("⚠️  Did not reach expected return flight page")
            print("📋 Extracting data from current page anyway...")
            # Still try to extract data from whatever page we're on
            current_content = await page.content()
            current_soup = BeautifulSoup(current_content, 'html.parser')
            return_flights = extract_return_flight_data(current_soup)
            workflow_data['return_flights'] = return_flights if return_flights else []
            
    except Exception as e:
        print(f"❌ Error in Select button workflow: {e}")
        
        # Save error page for debugging
        try:
            error_content = await page.content()
            error_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = f'select_workflow_error_{error_timestamp}.html'
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(error_content)
            print(f"💾 Error page saved as '{error_file}'")
        except:
            pass
    
    return workflow_data

if __name__ == "__main__":
    try:
        asyncio.run(search_and_continue())
    except KeyboardInterrupt:
        print("\n🛑 Script interrupted by user")
    except Exception as e:
        print(f"❌ Script failed: {e}")
