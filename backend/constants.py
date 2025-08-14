"""
Constants and mappings for restaurant search agents.
Contains country-specific review website mappings and helper functions.
"""

from typing import List, Optional, Dict

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
        "sites": ["https://yelp.com", "https://opentable.com", "https://tripadvisor.com", "https://zagat.com"],
        "descriptions": [
            "Yelp - Leading US review platform with extensive local coverage",
            "OpenTable - Restaurant reservations with reviews and ratings",
            "TripAdvisor - Global platform popular for tourist destinations",
            "Zagat - Premium dining reviews and ratings"
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

# Country detection patterns for location-based queries
COUNTRY_DETECTION_PATTERNS = {
    "japan": ["japan", "tokyo", "osaka", "kyoto", "hiroshima", "nagoya", "fukuoka", "sapporo", "yokohama", "kobe"],
    "united_states": ["usa", "america", "new york", "los angeles", "chicago", "san francisco", "miami", "boston", "seattle", "las vegas", "nyc", "la"],
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
DEFAULT_GLOBAL_SITES = ["https://yelp.com", "https://tripadvisor.com", "https://opentable.com", "https://google.com/maps"]


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
