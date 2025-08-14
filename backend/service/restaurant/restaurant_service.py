import json
import os
import hashlib
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv
import httpx

from ddgs import DDGS
from llama_index.llms.google_genai import GoogleGenAI
from service.restaurant.models import UserPreferences, Restaurant, RestaurantSearchResponse

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestaurantFinder:
    def __init__(self):
        self.ddgs = DDGS()
        
        # Simple in-memory cache
        self._cache = {}  # key: query_hash, value: (timestamp, results)
        self._cache_ttl = 900  # 15 minutes
        
        # Initialize OpenRouter client for GLM-4-32B
        self.openrouter_client = None
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if self.openrouter_api_key:
            self.openrouter_client = httpx.AsyncClient(
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Waypoint Travel App"
                }
            )
            logger.info("OpenRouter client initialized for GLM-4-32B")
        
        # Keep Google Gemini as fallback
        self.llm_client = None
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            self.llm_client = GoogleGenAI(
                model="models/gemini-2.5-flash",
                api_key=google_api_key,
                temperature=0.1,
                max_tokens=8192  # Increased from 4096
            )
            logger.info("Google Gemini 2.5 Flash LLM client initialized as fallback")
        
        if not self.openrouter_client and not self.llm_client:
            logger.warning("No LLM API keys found - running without LLM analysis")
    
    def build_mega_query(self, prefs: UserPreferences) -> str:
        query_parts = []
        
        # Simplified, more targeted query for actual restaurant pages
        food_type = prefs.food_type if prefs.food_type and prefs.food_type.lower() not in ["any", "na", "none"] else ""
        
        # Build a simpler, more focused query
        base_query = f"best {food_type} restaurants in {prefs.city}"
        query_parts.append(base_query)
        
        # Occasion (if provided and not NA)
        if prefs.occasion and prefs.occasion.lower() not in ["na", "none", "trip"]:
            query_parts.append(f'"{prefs.occasion}" OR "{prefs.occasion} dinner"')
        
        # Budget (simplified)
        if prefs.budget_level and prefs.budget_level in ["$", "$$", "$$$", "$$$$"]:
            budget_terms = {
                "$": "cheap budget affordable",
                "$$": "moderate mid-range",
                "$$$": "upscale fine dining",
                "$$$$": "luxury expensive"
            }
            query_parts.append(budget_terms[prefs.budget_level])
        
        # Dietary restrictions (filter out NA values)
        if prefs.dietary_restrictions:
            for dietary in prefs.dietary_restrictions:
                if dietary and dietary.lower() not in ["na", "none", ""]:
                    dietary_lower = dietary.lower()
                    if "vegetarian" in dietary_lower:
                        query_parts.append('"vegetarian options" OR "vegetarian menu"')
                    elif "vegan" in dietary_lower:
                        query_parts.append('"vegan options" OR "plant-based"')
                    elif "halal" in dietary_lower:
                        query_parts.append('"halal certified" OR "halal"')
                    elif "kosher" in dietary_lower:
                        query_parts.append('"kosher certified" OR "kosher"')
                    elif "gluten" in dietary_lower:
                        query_parts.append('"gluten-free" OR "gluten free options"')
        
        # Allergies (filter out NA values)
        if prefs.allergies:
            for allergy in prefs.allergies:
                if allergy and allergy.lower() not in ["na", "none", ""]:
                    allergy_lower = allergy.lower()
                    if "nut" in allergy_lower or "peanut" in allergy_lower:
                        query_parts.append('-peanut -nuts')
                    elif "shellfish" in allergy_lower:
                        query_parts.append('-shellfish -shrimp')
                    elif "dairy" in allergy_lower:
                        query_parts.append('-dairy -milk')
        
        # Ambiance preferences (filter out NA values)
        if prefs.preferred_ambiance:
            valid_ambiance = [amb for amb in prefs.preferred_ambiance if amb and amb.lower() not in ["na", "none", ""]]
            if valid_ambiance:
                ambiance_terms = ' OR '.join([f'"{amb}"' for amb in valid_ambiance])
                query_parts.append(f"({ambiance_terms})")
        
        # Must-have features (filter out NA values)
        if prefs.must_have:
            for must in prefs.must_have:
                if must and must.lower() not in ["na", "none", ""]:
                    query_parts.append(f'"{must}"')
        
        # Avoid list (filter out NA values)
        if prefs.avoid:
            for avoid in prefs.avoid:
                if avoid and avoid.lower() not in ["na", "none", ""]:
                    query_parts.append(f'-"{avoid}"')
        
        # Special requirements (filter out NA values)
        if prefs.special_requirements:
            for req in prefs.special_requirements:
                if req and req.lower() not in ["na", "none", ""]:
                    query_parts.append(f'"{req}"')
        
        # Time-specific (if provided and not NA)
        if prefs.time and prefs.time.lower() not in ["na", "none", ""]:
            query_parts.append(f'"open {prefs.time}" OR "{prefs.time} hours"')
        
        # Simplified - just add some review keywords
        query_parts.append("reviews menu address")
        
        # Determine country from city
        country = self._determine_country(prefs.city, prefs.country)
        # Update the region for DDGS search too
        prefs.country = country
        
        # Combine all parts
        mega_query = " ".join(filter(None, query_parts))
        
        # Log the query for debugging
        logger.info(f"Built mega query ({len(mega_query)} chars): {mega_query[:200]}...")
        
        return mega_query
    
    def _determine_country(self, city: str, provided_country: str = None) -> str:
        if provided_country and provided_country != "US":  # Default is US
            return provided_country
        
        # First try common cities for quick lookup
        city_lower = city.lower()
        common_cities = {
            "tokyo": "JP", "osaka": "JP", "kyoto": "JP", "yokohama": "JP", "nagoya": "JP",
            "seoul": "KR", "busan": "KR", "incheon": "KR",
            "bangkok": "TH", "phuket": "TH", "chiang mai": "TH",
            "singapore": "SG",
            "hong kong": "HK",
            "new york": "US", "los angeles": "US", "chicago": "US", "san francisco": "US", "boston": "US",
            "london": "GB", "manchester": "GB", "edinburgh": "GB",
            "paris": "FR", "lyon": "FR", "marseille": "FR",
            "rome": "IT", "milan": "IT", "venice": "IT", "florence": "IT",
            "berlin": "DE", "munich": "DE", "hamburg": "DE", "frankfurt": "DE"
        }
        
        for city_name, country_code in common_cities.items():
            if city_name in city_lower:
                return country_code
        
        # Use LLM for unknown cities
        if self.llm_client:
            try:
                return self._determine_country_with_llm(city)
            except Exception as e:
                logger.warning(f"LLM country detection failed for '{city}': {e}")
        
        # Default to US if LLM unavailable or fails
        return "US"
    
    def _determine_country_with_llm(self, city: str) -> str:
        """Use LLM to determine country code from city name with examples"""
        prompt = f"""Determine the ISO 3166-1 alpha-2 country code for the city: "{city}"

Examples:
- Tokyo → JP
- London → GB  
- Paris → FR
- Sydney → AU
- Toronto → CA
- Mumbai → IN
- São Paulo → BR
- Cairo → EG
- Dubai → AE
- Amsterdam → NL
- Stockholm → SE
- Mexico City → MX
- Buenos Aires → AR
- Lagos → NG
- Istanbul → TR
- Moscow → RU
- Beijing → CN
- Jakarta → ID
- Manila → PH
- Kuala Lumpur → MY
- Ho Chi Minh City → VN
- Casablanca → MA
- Nairobi → KE
- Tel Aviv → IL
- Athens → GR
- Prague → CZ
- Vienna → AT
- Zurich → CH
- Copenhagen → DK
- Oslo → NO
- Helsinki → FI
- Warsaw → PL
- Budapest → HU
- Bucharest → RO
- Sofia → BG
- Zagreb → HR
- Ljubljana → SI
- Bratislava → SK
- Tallinn → EE
- Riga → LV
- Vilnius → LT
- Reykjavik → IS
- Dublin → IE
- Brussels → BE
- Luxembourg → LU
- Lisbon → PT
- Madrid → ES
- Barcelona → ES
- Milan → IT
- Rome → IT
- Venice → IT
- Florence → IT
- Naples → IT
- Palermo → IT
- Genoa → IT
- Bologna → IT
- Turin → IT

Return ONLY the 2-letter country code (e.g., "US", "JP", "GB"). If uncertain, return "US"."""

        try:
            # Use LlamaIndex Google Gemini complete method
            response = self.llm_client.complete(prompt)
            
            country_code = response.text.strip().upper()
            
            # Validate it's a 2-letter code
            if len(country_code) == 2 and country_code.isalpha():
                logger.info(f"LLM determined country for '{city}': {country_code}")
                return country_code
            else:
                logger.warning(f"Invalid country code from LLM for '{city}': {country_code}")
                return "US"
                
        except Exception as e:
            logger.error(f"Error in LLM country detection for '{city}': {e}")
            raise
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cached_results(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if available and not expired"""
        cache_key = self._get_cache_key(query)
        if cache_key in self._cache:
            timestamp, results = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                logger.info(f"Cache hit for query hash: {cache_key}")
                return results
            else:
                # Remove expired cache
                del self._cache[cache_key]
        return None
    
    def _set_cached_results(self, query: str, results: List[Dict[str, Any]]):
        """Cache search results"""
        cache_key = self._get_cache_key(query)
        self._cache[cache_key] = (time.time(), results)
        logger.info(f"Cached results for query hash: {cache_key}")
    
    async def search_all_sources(self, query: str, prefs: UserPreferences) -> Dict[str, Any]:
        """Execute single DDGS text search for maximum results"""
        # Check cache first
        cached = self._get_cached_results(query)
        if cached:
            return {"text": cached, "cached": True}
        
        results = {
            "text": [],
            "cached": False
        }
        
        try:
            logger.info("Executing single DDGS search for restaurants...")
            
            # Single text search with max results
            region_map = {
                "JP": "jp-jp", "KR": "kr-kr", "TH": "th-th", "SG": "sg-en",
                "US": "us-en", "GB": "gb-en", "FR": "fr-fr", "IT": "it-it",
                "DE": "de-de", "HK": "hk-en", "CN": "cn-zh"
            }
            region = region_map.get(prefs.country, "wt-wt")
            
            # Single call to get 100 results
            text_results = self.ddgs.text(
                query,
                region=region,
                timelimit='y',  # Last year for more results
                max_results=100  # Get maximum results in one call
            )
            results["text"] = list(text_results) if text_results else []
            logger.info(f"Found {len(results['text'])} text results in single DDGS call")
            
            # Cache the results
            if results["text"]:
                self._set_cached_results(query, results["text"])
            
        except Exception as e:
            logger.error(f"DDGS search error: {e}")
        
        return results
    
    async def call_openrouter_llm(self, prompt: str, model: str = "z-ai/glm-4-32b") -> Optional[str]:
        """Call OpenRouter API with specified model"""
        if not self.openrouter_client:
            return None
        
        try:
            response = await self.openrouter_client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 16000,  # GLM-4-32B supports up to 16K output tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API error with {model}: {e}")
            return None
    
    async def llm_extract_restaurants(self, search_results: List[Dict[str, Any]], prefs: UserPreferences) -> List[Dict[str, Any]]:
        """Layer 1: Extract actual restaurants from search results"""
        if not search_results:
            return []
        
        # Prepare search results for LLM (reduced to 20 for better processing)
        results_text = "\n\n".join([
            f"Result {i+1}:\nTitle: {r.get('title', '')}\nBody: {r.get('body', '')}\nURL: {r.get('href', '')}"
            for i, r in enumerate(search_results[:20])  # Reduced from 50 to 20
        ])
        
        prompt = f"""Extract restaurant information from these search results for {prefs.city}.

For each ACTUAL RESTAURANT (not articles about restaurants), extract:
- name: Restaurant name
- cuisine: Type of food
- location: Address or area
- description: Brief description
- source_url: URL where found
- mentioned_features: Any mentioned features (rating, price, specialties, etc.)

Important: 
1. Return ONLY a JSON array
2. Include ONLY the TOP 10 actual restaurants
3. Exclude blog posts, articles, or platform homepages
4. No explanations before/after the JSON

Search Results:
{results_text[:8000]}  # Reduced from 12000

Return JSON array of top 10 restaurants. If no restaurants found, return empty array []."""
        
        # Try OpenRouter GLM-4-32B first
        response_text = None
        if self.openrouter_client:
            logger.info("Attempting restaurant extraction with GLM-4-32B via OpenRouter")
            response_text = await self.call_openrouter_llm(prompt, "z-ai/glm-4-32b")
        
        # Fallback to Gemini if OpenRouter fails
        if not response_text and self.llm_client:
            logger.info("Falling back to Google Gemini for restaurant extraction")
            try:
                response = self.llm_client.complete(prompt)
                response_text = response.text.strip()
            except Exception as e:
                logger.error(f"Gemini extraction error: {e}")
        
        if not response_text:
            logger.warning("No LLM available for extraction")
            return []
        
        try:
            # Clean up response to get JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Remove any non-JSON content before/after array
            response_text = response_text.strip()
            if not response_text.startswith('['):
                # Try to find the JSON array
                start_idx = response_text.find('[')
                if start_idx != -1:
                    response_text = response_text[start_idx:]
            if not response_text.endswith(']'):
                # Try to find the end of JSON array
                end_idx = response_text.rfind(']')
                if end_idx != -1:
                    response_text = response_text[:end_idx+1]
            
            extracted = json.loads(response_text)
            logger.info(f"LLM extracted {len(extracted)} restaurants from {len(search_results)} results")
            return extracted[:10]  # Ensure max 10 restaurants
            
        except Exception as e:
            logger.error(f"JSON parsing error: {e}")
            return []
    
    async def llm_enrich_restaurants(self, restaurants: List[Dict[str, Any]], prefs: UserPreferences) -> List[Dict[str, Any]]:
        """Layer 2: Enrich restaurant data by cross-referencing"""
        if not self.llm_client or not restaurants:
            return restaurants
        
        restaurants_json = json.dumps(restaurants[:50], indent=2)  # Limit for tokens
        
        prompt = f"""Enrich these restaurants with additional details for a user visiting {prefs.city}.

User preferences:
- Food type: {prefs.food_type}
- Party size: {prefs.party_size}
- Budget: {prefs.budget_level}
- Dietary: {', '.join(prefs.dietary_restrictions) if prefs.dietary_restrictions else 'None'}
- Allergies: {', '.join(prefs.allergies) if prefs.allergies else 'None'}

For each restaurant, add or infer:
- estimated_price_range: $ to $$$$
- best_for: What occasions/situations
- dietary_friendly: Boolean for dietary restrictions
- tourist_trap_risk: low/medium/high
- local_favorite: Boolean
- must_try_dishes: If mentioned
- reservation_needed: Boolean estimate

Restaurants:
{restaurants_json}

Return enriched JSON array with all original fields plus enrichments."""
        
        try:
            response = self.llm_client.chat.completions.create(
                model="google/gemini-2.5-flash-lite",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            enriched = json.loads(response_text)
            logger.info(f"LLM enriched {len(enriched)} restaurants")
            return enriched
            
        except Exception as e:
            logger.error(f"LLM enrichment error: {e}")
            return restaurants
    
    async def llm_rank_restaurants(self, restaurants: List[Dict[str, Any]], prefs: UserPreferences) -> List[Restaurant]:
        """Layer 3: Rank and score restaurants based on preferences"""
        if not self.llm_client or not restaurants:
            return self._convert_to_restaurant_objects(restaurants)
        
        restaurants_json = json.dumps(restaurants[:30], indent=2)
        
        prompt = f"""Rank these restaurants for this specific user.

User Profile:
- Location: {prefs.city}
- Food preference: {prefs.food_type}
- Party size: {prefs.party_size}
- Occasion: {prefs.occasion or 'casual dining'}
- Budget: {prefs.budget_level or 'flexible'}
- Dietary: {', '.join(prefs.dietary_restrictions) if prefs.dietary_restrictions else 'None'}
- Allergies: {', '.join(prefs.allergies) if prefs.allergies else 'None'}
- Must have: {', '.join(prefs.must_have) if prefs.must_have else 'None'}
- Avoid: {', '.join(prefs.avoid) if prefs.avoid else 'None'}
- Ambiance: {', '.join(prefs.preferred_ambiance) if prefs.preferred_ambiance else 'Any'}

For each restaurant provide:
- match_score: 0-10 based on ALL preferences
- authenticity_score: 0-10 for local/non-touristy
- why_recommended: Personalized 1-2 sentence reason
- potential_concerns: Any issues for this user
- booking_advice: Practical tips

Restaurants:
{restaurants_json}

Return JSON array sorted by match_score (highest first). Include top 15 only."""
        
        try:
            # Use LlamaIndex Google Gemini complete method
            response = self.llm_client.complete(prompt)
            
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            ranked = json.loads(response_text)
            logger.info(f"LLM ranked {len(ranked)} restaurants")
            
            # Convert to Restaurant objects
            return self._convert_ranked_to_restaurant_objects(ranked)
            
        except Exception as e:
            logger.error(f"LLM ranking error: {e}")
            return self._convert_to_restaurant_objects(restaurants[:15])
    
    def _fallback_to_basic_results(self, search_results: List[Dict[str, Any]]) -> List[Restaurant]:
        """Fallback to basic results when LLM fails"""
        restaurants = []
        for r in search_results:
            # Try to extract restaurant name from title
            title = r.get("title", "")
            name = title.split(" - ")[0].split(" | ")[0].strip() if title else "Unknown"
            
            if name and name != "Unknown":
                restaurants.append(Restaurant(
                    name=name,
                    description=r.get("body", "")[:500],
                    source_urls=[r.get("href")] if r.get("href") else []
                ))
        
        return restaurants if restaurants else [Restaurant(name="No results found")]
    
    def _convert_ranked_to_restaurant_objects(self, ranked: List[Dict[str, Any]]) -> List[Restaurant]:
        """Convert ranked restaurant data to Restaurant objects"""
        restaurants = []
        for r in ranked:
            # Ensure potential_concerns is always a list
            concerns = r.get("potential_concerns", [])
            if isinstance(concerns, str):
                concerns = [concerns] if concerns else []
            elif not isinstance(concerns, list):
                concerns = []
            
            restaurants.append(Restaurant(
                name=r.get("name", "Unknown"),
                address=r.get("location") or r.get("address"),
                description=r.get("description", "")[:500],
                source_urls=[r.get("source_url")] if r.get("source_url") else [],
                price_level=r.get("estimated_price_range"),
                rating=r.get("rating"),
                match_score=r.get("match_score"),
                authenticity_score=r.get("authenticity_score"),
                why_recommended=r.get("why_recommended"),
                potential_concerns=concerns,
                booking_advice=r.get("booking_advice")
            ))
        return restaurants
    
    async def process_with_llm_pipeline(self, search_results: List[Dict[str, Any]], prefs: UserPreferences) -> List[Restaurant]:
        """Process search results through 3-layer LLM pipeline"""
        if not self.llm_client or not search_results:
            # Fallback without LLM
            return self._fallback_to_basic_results(search_results[:15])
        
        # Layer 1: Extract restaurants from search results
        logger.info("LLM Pipeline - Layer 1: Extracting restaurants")
        extracted = await self.llm_extract_restaurants(search_results, prefs)
        
        if not extracted:
            logger.warning("No restaurants extracted, using fallback")
            return self._fallback_to_basic_results(search_results[:15])
        
        # Layer 2: Enrich restaurant data
        logger.info("LLM Pipeline - Layer 2: Enriching restaurant data")
        enriched = await self.llm_enrich_restaurants(extracted, prefs)
        
        # Layer 3: Rank restaurants
        logger.info("LLM Pipeline - Layer 3: Ranking restaurants")
        ranked = await self.llm_rank_restaurants(enriched, prefs)
        
        return ranked
    
    async def find_restaurants(self, preferences: UserPreferences, search_mode: str = "itinerary") -> RestaurantSearchResponse:
        start_time = datetime.now()
        
        # Build query based on mode
        if search_mode == "near_me":
            mega_query = self.build_near_me_query(preferences)
        else:
            mega_query = self.build_mega_query(preferences)
        
        # Search with single DDGS call
        search_results = await self.search_all_sources(mega_query, preferences)
        
        # Process through 3-layer LLM pipeline
        analyzed_restaurants = await self.process_with_llm_pipeline(
            search_results.get("text", []), 
            preferences
        )
        
        # Calculate search time
        search_time = (datetime.now() - start_time).total_seconds()
        
        return RestaurantSearchResponse(
            query_used=mega_query[:500] + "..." if len(mega_query) > 500 else mega_query,
            total_results_found=len(search_results.get("text", [])),
            restaurants=analyzed_restaurants,
            search_metadata={
                "search_time_seconds": search_time,
                "text_results": len(search_results.get("text", [])),
                "from_cache": search_results.get("cached", False),
                "llm_analysis": self.llm_client is not None,
                "search_mode": search_mode
            }
        )
    
    def build_near_me_query(self, prefs: UserPreferences) -> str:
        query_parts = []
        
        # Focus on immediate area
        query_parts.append(f"restaurant near {prefs.city} {prefs.food_type} open now")
        
        # Add walking distance markers
        query_parts.append('"walking distance" OR "nearby" OR "5 minutes" OR "close by"')
        
        # Current meal time
        if prefs.time:
            if "lunch" in prefs.time.lower() or "12" in prefs.time:
                query_parts.append('"lunch special" OR "lunch menu" OR "quick lunch"')
            elif "dinner" in prefs.time.lower() or "7" in prefs.time or "8" in prefs.time:
                query_parts.append('"dinner" OR "evening dining"')
        
        # Dietary needs (critical for immediate dining)
        for dietary in prefs.dietary_restrictions:
            query_parts.append(f'"{dietary} options available"')
        
        # Quick service markers
        if prefs.party_size == 1:
            query_parts.append('"counter seating" OR "bar seating" OR "no wait"')
        
        # Budget for immediate dining
        if prefs.budget_level:
            if prefs.budget_level in ["$", "$$"]:
                query_parts.append('"affordable" OR "cheap eats" OR "good value"')
        
        # Exclude chains if looking for local
        query_parts.append('-"chain restaurant" -"franchise"')
        
        # Add review sites
        country_sites = {
            "JP": "site:tabelog.com OR site:google.com/maps",
            "US": "site:yelp.com OR site:google.com/maps",
            "GB": "site:google.com/maps OR site:tripadvisor.co.uk"
        }
        
        if prefs.country in country_sites:
            query_parts.append(f"({country_sites[prefs.country]})")
        
        return " ".join(filter(None, query_parts))