#!/usr/bin/env python3
"""Test Amadeus API directly"""

import os
from pathlib import Path
from dotenv import load_dotenv
from amadeus import Client, ResponseError

# Load .env from root
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

client_id = os.getenv("AMADEUS_API_KEY")
client_secret = os.getenv("AMADEUS_Secret")

print(f"Client ID: {client_id}")
print(f"Client Secret: {'*' * (len(client_secret) - 4) + client_secret[-4:] if client_secret else 'Not set'}")

try:
    # Initialize Amadeus client
    amadeus = Client(
        client_id=client_id,
        client_secret=client_secret,
        hostname='test'  # Use test environment
    )
    
    print("\nTesting Amadeus API connection...")
    
    # Simple test - search for flights
    from datetime import datetime, timedelta
    future_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    print(f"Searching for flights on {future_date}")
    
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='JFK',
        destinationLocationCode='LAX',
        departureDate=future_date,
        adults=1,
        max=5
    )
    
    print(f"\nSuccess! Found {len(response.data)} flight offers")
    
    if response.data:
        first_offer = response.data[0]
        price = first_offer.get('price', {})
        print(f"\nFirst offer:")
        print(f"  Price: {price.get('currency')} {price.get('total')}")
        print(f"  Segments: {len(first_offer.get('itineraries', [{}])[0].get('segments', []))}")
        
except ResponseError as error:
    print(f"\nAmadeus API Error: {error}")
    if hasattr(error, 'response') and error.response:
        if hasattr(error.response, 'body'):
            print(f"Response body: {error.response.body}")
        if hasattr(error.response, 'result'):
            print(f"Response result: {error.response.result}")
except Exception as e:
    print(f"\nGeneral Error: {e}")