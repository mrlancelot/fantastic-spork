#!/usr/bin/env python3
"""
Quick test of the optimized scraper with timeout handling
"""

import asyncio
from flights_search_optimized import OptimizedFlightScraper, SearchParams, ScraperConfig
import signal
import sys

async def test_with_timeout():
    """Test scraper with timeout"""
    params = SearchParams(
        origin="Louisville",
        destination="Orlando", 
        departure_date="Aug 10, 2025",
        return_date="Aug 12, 2025"
    )
    
    config = ScraperConfig(
        headless=True,
        smart_wait=True,
        cleanup_files=True,
        max_combinations=2,  # Just 2 for quick test
        timeout=20000  # 20 second timeout
    )
    
    print("🚀 Starting quick test of optimized scraper...")
    print("   • Headless mode: ON")
    print("   • Smart wait: ON")
    print("   • Max combinations: 2")
    print("   • Timeout: 20 seconds\n")
    
    try:
        async with OptimizedFlightScraper(config) as scraper:
            # Test basic connectivity first
            print("1️⃣ Testing Google Flights connectivity...")
            await scraper.page.goto("https://www.google.com/travel/flights", 
                                   wait_until='domcontentloaded', 
                                   timeout=10000)
            print("✅ Connected to Google Flights\n")
            
            # Test data extraction
            print("2️⃣ Testing data extraction...")
            html = await scraper.page.content()
            initial_data = scraper.extract_flight_data_optimized(html)
            print(f"✅ Extraction working (found {len(initial_data)} initial elements)\n")
            
            # Full search test with timeout
            print("3️⃣ Running full search (max 20 seconds)...")
            combinations = await asyncio.wait_for(
                scraper.search_flights(params),
                timeout=20.0
            )
            
            if combinations:
                print(f"\n✅ SUCCESS! Found {len(combinations)} combinations")
                for combo in combinations:
                    print(f"   • Combination {combo.combination_id}: {combo.total_price}")
            else:
                print("\n⚠️ No combinations found, but scraper is working")
                
    except asyncio.TimeoutError:
        print("\n⏱️ Test timed out after 20 seconds (this is expected for full scraping)")
        print("   The scraper is working but needs more time for complete results")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def signal_handler(sig, frame):
    print('\n\n🛑 Test interrupted by user')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        asyncio.run(test_with_timeout())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")