import os
import requests
import httpx
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

class APIUtils:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable required")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Travel Search"
        }
        
    async def generate_flight_urls(self, origin: str, destination: str, departure_date: str, return_date: Optional[str], adults: int, travel_class: str) -> List[Dict]:
        query = f"Get me all the flights from {departure_date}"
        if return_date:
            query += f" to {return_date}"
        query += f" from {origin} to {destination} and nearby airports with the exact urls from kayak.com"
        
        prompt = f"""For the query: {query}
Generate the direct search URL(s) for flight booking websites. Focus on constructing the actual URLs with proper parameters.

Return ONLY the XML format with no additional text or explanation:
<results>
<result>
    <title>Flight Search URL</title>
    <link>Direct URL with search parameters</link>
    <description>Flight search details</description>
    <last_updated>Current date</last_updated>
</result>
</results>

Construct URLs with proper date formats, airport codes, and search parameters. Do not include any introductory text or explanations."""
        
        payload = {
            "model": "z-ai/glm-4-32b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        xml_content = data['choices'][0]['message']['content']
        
        return self._parse_xml_urls(xml_content)
    
    async def generate_hotel_urls(self, destination: str, check_in: str, check_out: str, adults: int, rooms: int) -> List[Dict]:
        print(f"DEBUG APIUtils: Generating hotel URLs for {destination}, {check_in} to {check_out}")
        query = f"Get me all the Hotels from {check_in} to {check_out} in or near {destination} with the exact working urls"
        print(f"DEBUG APIUtils: Query: {query}")
        
        prompt = f"""For the query: {query}
Generate the direct search URL(s) for hotel and accommodation booking websites (Booking.com and Airbnb). Focus on constructing the actual URLs with proper parameters.

Return ONLY the XML format with no additional text or explanation:
<results>
<result>
    <title>Hotel/Airbnb Search URL</title>
    <link>Direct URL with search parameters</link>
    <description>Accommodation search details (location, dates, guests, property type)</description>
    <last_updated>Current date</last_updated>
</result>
</results>

Construct URLs with proper date formats (YYYY-MM-DD), location parameters, guest counts, room requirements, and property type filters. Include multiple booking platforms when relevant. Do not include any introductory text or explanations."""
        
        payload = {
            "model": "google/gemini-2.5-flash-lite",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        print(f"DEBUG APIUtils: Sending request to OpenRouter API...")
        print(f"DEBUG APIUtils: Using model: {payload['model']}")
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        print(f"DEBUG APIUtils: Response status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        xml_content = data['choices'][0]['message']['content']
        print(f"DEBUG APIUtils: Received XML content ({len(xml_content)} chars)")
        print(f"DEBUG APIUtils: XML Preview: {xml_content[:500]}...")
        
        result = self._parse_xml_urls(xml_content)
        print(f"DEBUG APIUtils: Parsed {len(result)} URLs from XML")
        return result
    
    def _parse_xml_urls(self, xml_content: str) -> List[Dict]:
        print(f"DEBUG _parse_xml_urls: Starting to parse XML")
        results = []
        try:
            # Clean up the XML content if needed
            xml_content = xml_content.strip()
            if not xml_content.startswith('<'):
                print(f"DEBUG _parse_xml_urls: Content doesn't start with '<', looking for XML...")
                # Try to find XML within the content
                start_idx = xml_content.find('<results>')
                if start_idx != -1:
                    xml_content = xml_content[start_idx:]
                    end_idx = xml_content.find('</results>') + len('</results>')
                    if end_idx > len('</results>') - 1:
                        xml_content = xml_content[:end_idx]
                    print(f"DEBUG _parse_xml_urls: Extracted XML from content")
            
            print(f"DEBUG _parse_xml_urls: Attempting to parse: {xml_content[:200]}...")
            root = ET.fromstring(xml_content)
            for result in root.findall('.//result'):
                title_elem = result.find('title')
                link_elem = result.find('link')
                desc_elem = result.find('description')
                
                if link_elem is not None and link_elem.text:
                    url_data = {
                        'title': title_elem.text if title_elem is not None else '',
                        'url': link_elem.text,
                        'description': desc_elem.text if desc_elem is not None else '',
                        'platform': self._extract_platform(link_elem.text)
                    }
                    results.append(url_data)
                    print(f"DEBUG _parse_xml_urls: Found URL - {url_data['platform']}: {url_data['url'][:80]}...")
        except ET.ParseError as e:
            print(f"DEBUG _parse_xml_urls: XML ParseError: {str(e)}")
            print(f"DEBUG _parse_xml_urls: Failed XML content: {xml_content[:500]}...")
        except Exception as e:
            print(f"DEBUG _parse_xml_urls: Unexpected error: {type(e).__name__}: {str(e)}")
        
        print(f"DEBUG _parse_xml_urls: Returning {len(results)} parsed URLs")
        return results
    
    def _extract_platform(self, url: str) -> str:
        if 'kayak.com' in url:
            return 'kayak'
        elif 'booking.com' in url:
            return 'booking'
        elif 'airbnb.com' in url:
            return 'airbnb'
        return 'unknown'
    
    async def scrape_url(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            return response.text
    
    async def scrape_urls_parallel(self, urls: List[str]) -> List[str]:
        print(f"DEBUG scrape_urls_parallel: Scraping {len(urls)} URLs in parallel")
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception))
        print(f"DEBUG scrape_urls_parallel: Successfully scraped {successful}/{len(urls)} pages")
        return results
    
    async def generate_flight_metadata(self, origin: str, destination: str, departure_date: str, return_date: Optional[str], adults: int, travel_class: str) -> List[Dict]:
        prompt = f"""Generate realistic flight options for this route.

Route: {origin} to {destination}
Departure: {departure_date}
Return: {return_date if return_date else 'One-way'}
Passengers: {adults} adults
Class: {travel_class}

Return ONLY a JSON array with 3-5 realistic flight options in this exact format:
[{{
    "airline": "Air France",
    "price": 2850,
    "price_formatted": "$2,850",
    "departure_time": "10:30 AM",
    "arrival_time": "8:45 PM +1",
    "duration": "28h 15m",
    "stops": 2,
    "layover": "AMS 2h 30m, SCL 3h 45m",
    "origin": "CDG",
    "destination": "PUQ",
    "flight_type": "outbound",
    "note": "Generated estimate - click search URL for live prices"
}}]

Include realistic airlines, times, and connections for this route."""
        
        payload = {
            "model": "z-ai/glm-4-32b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            try:
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                flights = json.loads(content.strip())
                if isinstance(flights, list):
                    return flights
            except json.JSONDecodeError:
                pass
        
        return []
    
    async def extract_flight_data(self, html_contents: List[str], urls: List[str]) -> List[Dict]:
        all_flights = []
        
        for html, url in zip(html_contents, urls):
            if isinstance(html, Exception):
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)[:10000]
            
            prompt = f"""Extract flight information from this Kayak search page content and return ONLY a JSON array of flights.

Content: {text_content}

Return ONLY valid JSON in this exact format:
[{{
    "airline": "Airline name",
    "price": 1234,
    "price_formatted": "$1,234",
    "departure_time": "8:45 AM",
    "arrival_time": "10:30 PM",
    "duration": "19h 45m",
    "stops": 1,
    "layover": "BOG 2h 31m",
    "origin": "CDG",
    "destination": "SCL",
    "flight_type": "outbound"
}}]"""
            
            payload = {
                "model": "z-ai/glm-4-32b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                try:
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    
                    flights = json.loads(content.strip())
                    if isinstance(flights, list):
                        for flight in flights:
                            flight['source_url'] = url
                        all_flights.extend(flights)
                except json.JSONDecodeError:
                    pass
        
        return all_flights
    
    async def extract_hotel_data(self, html_contents: List[str], urls: List[str]) -> List[Dict]:
        print(f"DEBUG extract_hotel_data: Processing {len(html_contents)} HTML pages")
        all_hotels = []
        
        for idx, (html, url) in enumerate(zip(html_contents, urls)):
            if isinstance(html, Exception):
                print(f"DEBUG extract_hotel_data: Page {idx+1} failed to scrape: {html}")
                continue
            print(f"DEBUG extract_hotel_data: Processing page {idx+1} from {url[:80]}...")
            
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)[:10000]
            
            platform = 'booking' if 'booking.com' in url else 'airbnb'
            
            prompt = f"""Extract hotel/accommodation information from this {platform} search page content and return ONLY a JSON array.

Content: {text_content}

Return ONLY valid JSON in this exact format:
[{{
    "name": "Hotel Name",
    "price": 150,
    "price_formatted": "$150",
    "rating": 8.5,
    "reviews_count": 234,
    "location": "City Center, Tokyo",
    "amenities": ["WiFi", "Pool", "Gym"],
    "source": "{platform}.com"
}}]"""
            
            payload = {
                "model": "z-ai/glm-4-32b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            print(f"DEBUG extract_hotel_data: Sending extraction request to AI...")
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            print(f"DEBUG extract_hotel_data: AI response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                try:
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    
                    hotels = json.loads(content.strip())
                    if isinstance(hotels, list):
                        print(f"DEBUG extract_hotel_data: Extracted {len(hotels)} hotels from page {idx+1}")
                        for hotel in hotels:
                            hotel['source_url'] = url
                        all_hotels.extend(hotels)
                    else:
                        print(f"DEBUG extract_hotel_data: Response was not a list: {type(hotels)}")
                except json.JSONDecodeError as e:
                    print(f"DEBUG extract_hotel_data: JSON decode error: {str(e)}")
                    print(f"DEBUG extract_hotel_data: Content was: {content[:200]}...")
            else:
                print(f"DEBUG extract_hotel_data: AI request failed with status {response.status_code}")
        
        print(f"DEBUG extract_hotel_data: Total hotels extracted: {len(all_hotels)}")
        return all_hotels