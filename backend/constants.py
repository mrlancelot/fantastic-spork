"""
Constants and mappings for restaurant search agents.
Contains country-specific review website mappings and helper functions.
"""

from typing import List, Optional, Dict, Any

# Country-specific review website mapping for targeted searches
COUNTRY_REVIEW_SITES = {
    "japan": {
        "sites": ["https://tabelog.com/en/", "https://reddit.com", "https://youtube.com"],
        "descriptions": [
            "Tabelog - Most trusted restaurant review site in Japan with detailed ratings and photos",
            "Reddit - Social platform with restaurant recommendations",
            "YouTube - Video platform with restaurant reviews"
        ]
    },
    "united_states": {
        "sites": ["https://yelp.com"],
        "descriptions": [
            "Yelp - Leading US review platform with extensive local coverage"
        ]
    },
    "united_kingdom": {
        "sites": ["https://tripadvisor.co.uk", "https://opentable.co.uk", "https://timeout.com", "https://squaremeal.co.uk"],
        "descriptions": [
            "TripAdvisor UK - Popular review platform for UK restaurants",
            "OpenTable UK - Restaurant bookings with reviews",
            "Time Out - Curated restaurant guides and reviews",
            "Square Meal - Fine dining and restaurant reviews"
        ]
    },
    "france": {
        "sites": ["https://tripadvisor.fr", "https://lafourchette.com", "https://michelin.com", "https://lebonbon.fr"],
        "descriptions": [
            "TripAdvisor France - French restaurant reviews and ratings",
            "LaFourchette - Restaurant reservations and reviews in France",
            "Michelin Guide - Premium fine dining reviews and stars",
            "Le Bonbon - Local Parisian restaurant recommendations"
        ]
    },
    "italy": {
        "sites": ["https://tripadvisor.it", "https://thefork.it", "https://gamberorosso.it", "https://agrodolce.it"],
        "descriptions": [
            "TripAdvisor Italy - Italian restaurant reviews",
            "TheFork Italy - Restaurant bookings and reviews",
            "Gambero Rosso - Authoritative Italian food and restaurant guide",
            "Agrodolce - Italian culinary magazine with restaurant reviews"
        ]
    },
    "germany": {
        "sites": ["https://tripadvisor.de", "https://opentable.de", "https://restaurant-kritik.de", "https://falstaff.de"],
        "descriptions": [
            "TripAdvisor Germany - German restaurant reviews",
            "OpenTable Germany - Restaurant reservations with reviews",
            "Restaurant-Kritik - German restaurant criticism and reviews",
            "Falstaff - Premium dining and wine guide"
        ]
    },
    "china": {
        "sites": ["https://dianping.com", "https://meituan.com", "https://xiaohongshu.com"],
        "descriptions": [
            "Dianping - China's largest restaurant review platform",
            "Meituan - Food delivery and restaurant reviews",
            "Xiaohongshu - Social platform with restaurant recommendations"
        ]
    },
    "south_korea": {
        "sites": ["https://mangoplate.com", "https://yogiyo.co.kr", "https://siksinhot.com"],
        "descriptions": [
            "MangoPlate - Korea's top restaurant discovery platform",
            "Yogiyo - Food delivery with restaurant reviews",
            "SiksinHot - Popular Korean restaurant review site"
        ]
    },  
    "australia": {
        "sites": ["https://tripadvisor.com.au", "https://opentable.com.au", "https://urbanspoon.com.au", "https://goodfood.com.au"],
        "descriptions": [
            "TripAdvisor Australia - Australian restaurant reviews",
            "OpenTable Australia - Restaurant bookings and reviews",
            "Urbanspoon Australia - Local restaurant discovery",
            "Good Food - Sydney Morning Herald restaurant guide"
        ]
    },
    "canada": {
        "sites": ["https://tripadvisor.ca", "https://opentable.ca", "https://yelp.ca", "https://blogto.com"],
        "descriptions": [
            "TripAdvisor Canada - Canadian restaurant reviews",
            "OpenTable Canada - Restaurant reservations with reviews",
            "Yelp Canada - Local business and restaurant reviews",
            "BlogTO - Toronto restaurant and food scene coverage"
        ]
    }
}

# Country to currency mapping
COUNTRY_CURRENCY = {
    "japan": "¥",
    "united_states": "$",
    "united_kingdom": "£",
    "france": "€",
    "italy": "€",
    "germany": "€",
    "china": "¥",
    "south_korea": "₩",
    "australia": "A$",
    "canada": "C$"
}

# Country detection patterns for location-based queries
COUNTRY_DETECTION_PATTERNS = {
    "japan": ["japan", "tokyo", "osaka", "kyoto", "hiroshima", "nagoya", "fukuoka", "sapporo", "yokohama", "kobe", "hokkaido", "sendai", "kanagawa", "aichi", "hyogo", "chiba", "saitama", "shizuoka", "niigata", "gifu", "fukushima", "okayama", "mie", "kagoshima", "yamaguchi", "nagano", "miyagi", "ibaraki", "nara", "kumamoto", "ehime", "kagawa", "oita", "yamagata", "iwate", "tochigi", "miyazaki", "wakayama", "gunma", "ishikawa", "okinawa", "aomori", "saga", "kochi", "fukui", "tokushima", "toyama", "akita", "tottori", "shimane"],
    "united_states": ["usa", "america", "new york", "los angeles", "chicago", "san francisco", "miami", "boston", "seattle", "las vegas", "nyc", "la", "sf"],
    "united_kingdom": ["uk", "britain", "london", "manchester", "birmingham", "glasgow", "edinburgh", "liverpool", "bristol"],
    "france": ["france", "paris", "lyon", "marseille", "toulouse", "nice", "nantes", "strasbourg", "montpellier"],
    "italy": ["italy", "rome", "milan", "naples", "turin", "palermo", "genoa", "bologna", "florence", "venice"],
    "germany": ["germany", "berlin", "munich", "hamburg", "cologne", "frankfurt", "stuttgart", "düsseldorf", "dortmund"],
    "china": ["china", "beijing", "shanghai", "guangzhou", "shenzhen", "tianjin", "wuhan", "xi'an", "chengdu", "hangzhou"],
    "south_korea": ["korea", "seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "ulsan"],
    "australia": ["australia", "sydney", "melbourne", "brisbane", "perth", "adelaide", "gold coast", "canberra"],
    "canada": ["canada", "toronto", "vancouver", "montreal", "calgary", "ottawa", "edmonton", "quebec city", "winnipeg"]
}

# Price range filters for restaurant searches
PRICE_RANGE_FILTERS = {
    "budget": "budget-friendly restaurants under $25 per person",
    "mid_range": "mid-range restaurants $25-50 per person", 
    "upscale": "upscale restaurants $50+ per person"
}

# Default global review sites when country not detected
DEFAULT_GLOBAL_SITES = ["https://yelp.com", "https://opentable.com"]

# Japan-specific Tabelog area mappings for targeted URL construction
TABELOG_AREA_MAPPING = {
    # Major cities (direct paths)
    "tokyo": "tokyo",
    "osaka": "osaka", 
    "kyoto": "kyoto",
    "fukuoka": "fukuoka",
    "hokkaido": "hokkaido",
    "sapporo": "hokkaido",  # Sapporo is in Hokkaido
    "aichi": "aichi",
    "nagoya": "aichi",  # Nagoya is in Aichi
    
    # Hokkaido/Tohoku region
    "aomori": "aomori",
    "iwate": "iwate", 
    "miyagi": "miyagi",
    "sendai": "miyagi",  # Sendai is in Miyagi
    "akita": "akita",
    "yamagata": "yamagata",
    "fukushima": "fukushima",
    
    # Kanto region
    "ibaraki": "ibaraki",
    "tochigi": "tochigi",
    "gunma": "gunma",
    "saitama": "saitama",
    "chiba": "chiba",
    "kanagawa": "kanagawa",
    "yokohama": "kanagawa",  # Yokohama is in Kanagawa
    
    # Chubu region
    "niigata": "niigata",
    "toyama": "toyama",
    "ishikawa": "ishikawa",
    "fukui": "fukui",
    "yamanashi": "yamanashi",
    "nagano": "nagano",
    "gifu": "gifu",
    "shizuoka": "shizuoka",
    "mie": "mie",
    
    # Kansai region
    "shiga": "shiga",
    "hyogo": "hyogo",
    "kobe": "hyogo",  # Kobe is in Hyogo
    "nara": "nara",
    "wakayama": "wakayama",
    
    # Chugoku/Shikoku region
    "tottori": "tottori",
    "shimane": "shimane",
    "okayama": "okayama",
    "hiroshima": "hiroshima",
    "yamaguchi": "yamaguchi",
    "tokushima": "tokushima",
    "kagawa": "kagawa",
    "ehime": "ehime",
    "kochi": "kochi",
    
    # Kyushu/Okinawa region
    "saga": "saga",
    "nagasaki": "nagasaki",
    "kumamoto": "kumamoto",
    "oita": "oita",
    "miyazaki": "miyazaki",
    "kagoshima": "kagoshima",
    "okinawa": "okinawa",
    
    # Generic fallbacks
    "japan": "tokyo",  # Default to Tokyo for generic Japan queries
}

# Tabelog budget range mappings (thousands of yen)
TABELOG_BUDGET_MAPPING = {
    "1-4": {"min": 1, "max": 4, "description": "Budget dining (¥1,000-4,000)"},
    "4-8": {"min": 4, "max": 8, "description": "Mid-range dining (¥4,000-8,000)"},
    "8-16": {"min": 8, "max": 16, "description": "Upscale dining (¥8,000-16,000)"},
    # Alternative budget formats
    "budget": {"min": 1, "max": 4, "description": "Budget dining (¥1,000-4,000)"},
    "mid_range": {"min": 4, "max": 8, "description": "Mid-range dining (¥4,000-8,000)"},
    "upscale": {"min": 8, "max": 16, "description": "Upscale dining (¥8,000-16,000)"},
}


def detect_country_from_query(query: str) -> Optional[str]:
    """Detect country from query text using common city/country keywords."""
    query_lower = query.lower()
    
    for country, keywords in COUNTRY_DETECTION_PATTERNS.items():
        if any(keyword in query_lower for keyword in keywords):
            return country
    
    return None


def get_country_specific_sites(country: str) -> List[str]:
    """Get review sites specific to a country."""
    if country in COUNTRY_REVIEW_SITES:
        return COUNTRY_REVIEW_SITES[country]["sites"]
    # Default to global sites if country not found
    return DEFAULT_GLOBAL_SITES


def build_country_aware_search_query(base_query: str, country_sites: List[str] = None, price_range: str = None) -> str:
    """Build search query with country-specific review sites and price filtering.
    
    Returns:
        dict: Contains 'query' and 'include_domains' keys for tavily_search
    """
    query = base_query
    
    # Add price range filtering if specified
    if price_range:
        price_filter = get_price_range_filter(price_range)
        if price_filter:
            query = f"{query} {price_filter}"
    
    # Return query and include_domains with full URLs
    if country_sites:
        return str({
            'query': f"{query} restaurant reviews",
            'include_domains': country_sites
        })
    else:
        # Default global search domains with full URLs
        return str({
            'query': f"{query} restaurant reviews", 
            'include_domains': ['https://yelp.com', 'https://tripadvisor.com', 'https://opentable.com']
        })


def get_price_range_filter(price_range: str) -> Optional[str]:
    """Get price range filter description."""
    return PRICE_RANGE_FILTERS.get(price_range)


def get_country_descriptions(country: str) -> List[str]:
    """Get descriptions of review sites for a specific country."""
    if country in COUNTRY_REVIEW_SITES:
        return COUNTRY_REVIEW_SITES[country]["descriptions"]
    return []


def extract_japan_location(query: str) -> str:
    """Extract location from Japan-related query and map to Tabelog area.
    
    Args:
        query: User query string
        
    Returns:
        str: Tabelog area path (defaults to 'tokyo' if not found)
    """
    query_lower = query.lower()
    
    # Check for specific cities/areas in the query
    for location, tabelog_area in TABELOG_AREA_MAPPING.items():
        if location in query_lower:
            return tabelog_area
    
    # Default to Tokyo if no specific location found
    return "tokyo"


def extract_japan_budget(query: str) -> Optional[dict]:
    """Extract budget range from Japan-related query.
    
    Args:
        query: User query string
        
    Returns:
        dict: Budget mapping with min, max, description or None if not found
    """
    query_lower = query.lower()
    
    # Check for explicit budget ranges
    for budget_key, budget_info in TABELOG_BUDGET_MAPPING.items():
        if budget_key.replace('_', ' ') in query_lower or budget_key.replace('-', ' to ') in query_lower:
            return budget_info
    
    # Check for budget keywords
    if any(word in query_lower for word in ['cheap', 'budget', 'affordable', 'inexpensive']):
        return TABELOG_BUDGET_MAPPING["budget"]
    elif any(word in query_lower for word in ['expensive', 'upscale', 'fine dining', 'luxury']):
        return TABELOG_BUDGET_MAPPING["upscale"]
    elif any(word in query_lower for word in ['mid range', 'moderate', 'medium']):
        return TABELOG_BUDGET_MAPPING["mid_range"]
    
    return None


def build_tabelog_url(area: str, budget_info: dict = None) -> str:
    """Build Tabelog URL with area and budget parameters.
    
    Args:
        area: Tabelog area path (e.g., 'tokyo', 'osaka')
        budget_info: Budget mapping dict with 'min' and 'max' keys
        
    Returns:
        str: Complete Tabelog URL with parameters
    """
    base_url = f"https://tabelog.com/en/{area}/rstLst/"
    
    # Standard parameters for dinner, sorted by rating
    params = {
        "RdoCosTp": "2",  # Dinner pricing
        "SrtT": "rt"       # Sort by rating (highest first)
    }
    
    # Add budget parameters if provided
    if budget_info:
        params["LstCos"] = str(budget_info["min"])
        params["LstCosT"] = str(budget_info["max"])
    
    # Construct query string
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    
    return f"{base_url}?{query_string}"


def extract_japan_query_params(query: str) -> dict:
    """Extract location and budget parameters from Japan-related query.
    
    Args:
        query: User query string
        
    Returns:
        dict: Contains 'area', 'budget_info', and 'tabelog_url' keys
    """
    area = extract_japan_location(query)
    budget_info = extract_japan_budget(query)
    tabelog_url = build_tabelog_url(area, budget_info)
    
    return {
        "area": area,
        "budget_info": budget_info,
        "tabelog_url": tabelog_url,
        "budget_description": budget_info["description"] if budget_info else "All price ranges"
    }


def extract_city_from_query(query: str, country: str = None) -> Optional[str]:
    """Extract city name from query for any country.
    
    Args:
        query: User query string
        country: Optional country hint
        
    Returns:
        str: Extracted city name or None
    """
    query_lower = query.lower()
    
    # If country is provided, check its specific patterns
    if country and country in COUNTRY_DETECTION_PATTERNS:
        for keyword in COUNTRY_DETECTION_PATTERNS[country]:
            if keyword in query_lower and len(keyword) > 3:  # Skip short country codes
                # Check if it's a city name (not country name)
                if keyword not in ['usa', 'uk', 'america', 'britain', 'france', 'italy', 'germany', 'china', 'korea', 'australia', 'canada', 'japan']:
                    return keyword.title()
    
    # If no country provided or city not found, check all patterns
    for country_key, keywords in COUNTRY_DETECTION_PATTERNS.items():
        for keyword in keywords:
            if keyword in query_lower and len(keyword) > 3:
                # Check if it's a city name (not country name)
                if keyword not in ['usa', 'uk', 'america', 'britain', 'france', 'italy', 'germany', 'china', 'korea', 'australia', 'canada', 'japan']:
                    return keyword.title()
    
    return None


def get_country_currency(country: str) -> str:
    """Get the currency symbol for a country.
    
    Args:
        country: Country identifier
        
    Returns:
        str: Currency symbol (defaults to $ if not found)
    """
    return COUNTRY_CURRENCY.get(country, "$")


def build_international_search_query(query: str, city: str = None, country: str = None, price_range: str = None) -> dict:
    """Build search query for international restaurant searches.
    
    Args:
        query: Original user query
        city: Extracted city name
        country: Detected country
        price_range: Optional price range filter
        
    Returns:
        dict: Query parameters for tavily_search including query and include_domains
    """
    # Build base query with city
    if city:
        # Extract cuisine type if mentioned
        query_lower = query.lower()
        cuisine_found = None
        for cuisine in ['italian', 'chinese', 'japanese', 'french', 'thai', 'indian', 'mexican', 'korean', 'vietnamese', 'american']:
            if cuisine in query_lower:
                cuisine_found = cuisine
                break
        
        # Build query in the format: "best [cuisine] budget-friendly restaurants in [city] under $X per person"
        if price_range == "budget" or "budget" in query_lower:
            if cuisine_found:
                search_query = f"best {cuisine_found} budget-friendly restaurants in {city} under $25 per person"
            else:
                search_query = f"best budget-friendly restaurants in {city} under $25 per person"
        elif price_range == "mid_range":
            if cuisine_found:
                search_query = f"best {cuisine_found} restaurants in {city} $25-50 per person"
            else:
                search_query = f"best restaurants in {city} $25-50 per person"
        elif price_range == "upscale":
            if cuisine_found:
                search_query = f"best {cuisine_found} upscale restaurants in {city} $50+ per person"
            else:
                search_query = f"best upscale restaurants in {city} $50+ per person"
        else:
            # No specific price range
            if cuisine_found:
                search_query = f"best {cuisine_found} restaurants in {city}"
            else:
                search_query = f"best restaurants in {city}"
    else:
        search_query = query
    
    # Get country-specific review sites
    review_sites = []
    if country and country in COUNTRY_REVIEW_SITES:
        review_sites = COUNTRY_REVIEW_SITES[country]["sites"]
    else:
        review_sites = DEFAULT_GLOBAL_SITES
    
    return {
        "query": search_query,
        "include_domains": review_sites
    }
