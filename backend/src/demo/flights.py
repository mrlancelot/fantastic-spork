import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import time

async def scrape_google_flights():
    """Scrape Google Flights for SFO to Tokyo flights"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # Navigate to Google Flights
            print("Navigating to Google Flights...")
            await page.goto('https://www.google.com/travel/flights', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # Handle potential cookie consent
            try:
                cookie_button = page.locator('button:has-text("Accept all")')
                if await cookie_button.is_visible(timeout=5000):
                    await cookie_button.click()
                    await page.wait_for_timeout(2000)
            except:
                pass
            
            # Fill departure airport (SFO)
            print("Setting departure airport to SFO...")
            departure_input = page.locator('input[placeholder*="Where from"], input[aria-label*="Where from"], input[placeholder*="From"]').first
            await departure_input.click()
            await departure_input.fill('SFO')
            await page.wait_for_timeout(2000)
            
            # Select SFO from dropdown
            sfo_option = page.locator('li:has-text("San Francisco"), div:has-text("SFO")').first
            await sfo_option.click()
            await page.wait_for_timeout(1000)
            
            # Fill destination airport (Tokyo)
            print("Setting destination to Tokyo...")
            destination_input = page.locator('input[placeholder*="Where to"], input[aria-label*="Where to"], input[placeholder*="To"]').first
            await destination_input.click()
            await destination_input.fill('Tokyo')
            await page.wait_for_timeout(2000)
            
            # Select Tokyo from dropdown (NRT or HND)
            tokyo_option = page.locator('li:has-text("Tokyo"), div:has-text("NRT"), div:has-text("HND")').first
            await tokyo_option.click()
            await page.wait_for_timeout(1000)
            
            # Set dates - today to next week
            today = datetime.now()
            next_week = today + timedelta(days=7)
            
            print(f"Setting dates: {today.strftime('%Y-%m-%d')} to {next_week.strftime('%Y-%m-%d')}...")
            
            # Click on departure date
            departure_date_button = page.locator('input[placeholder*="Departure"], button[aria-label*="Departure"]').first
            await departure_date_button.click()
            await page.wait_for_timeout(2000)
            
            # Navigate to current month and select today's date
            today_selector = f'div[data-iso="{today.strftime("%Y-%m-%d")}"], button[aria-label*="{today.strftime("%B %d")}"]'
            today_element = page.locator(today_selector).first
            if await today_element.is_visible(timeout=5000):
                await today_element.click()
            else:
                # Fallback: click on any available date close to today
                available_date = page.locator('div[role="button"]:not([aria-disabled="true"])').first
                await available_date.click()
            
            await page.wait_for_timeout(1000)
            
            # Select return date (next week)
            next_week_selector = f'div[data-iso="{next_week.strftime("%Y-%m-%d")}"], button[aria-label*="{next_week.strftime("%B %d")}"]'
            next_week_element = page.locator(next_week_selector).first
            if await next_week_element.is_visible(timeout=5000):
                await next_week_element.click()
            else:
                # Fallback: click on a date 7 days from the selected departure
                future_dates = page.locator('div[role="button"]:not([aria-disabled="true"])')
                count = await future_dates.count()
                if count > 7:
                    await future_dates.nth(7).click()
                else:
                    await future_dates.last.click()
            
            await page.wait_for_timeout(1000)
            
            # Confirm date selection
            done_button = page.locator('button:has-text("Done"), button:has-text("OK")')
            if await done_button.is_visible(timeout=3000):
                await done_button.click()
                await page.wait_for_timeout(1000)
            
            # Click Explore button
            print("Clicking Explore button...")
            explore_button = page.locator('button:has-text("Explore"), button[aria-label*="Search"]').first
            await explore_button.click()
            
            # Wait for results to load
            print("Waiting for flight results...")
            await page.wait_for_timeout(10000)  # Wait for results to load
            
            # Wait for flight results container
            await page.wait_for_selector('div[data-testid="flight-results"], li[data-testid="flight-offer"], div[jsname], .pIav2d', timeout=30000)
            
            # Extract flight information
            print("Extracting flight information...")
            flights = []
            
            # Try multiple selectors for flight cards
            flight_selectors = [
                'li[data-testid="flight-offer"]',
                'div[jsname] div[role="listitem"]',
                '.pIav2d',
                'div[data-testid="flight-card"]',
                '[data-testid*="flight"]'
            ]
            
            flight_elements = None
            for selector in flight_selectors:
                elements = page.locator(selector)
                count = await elements.count()
                if count > 0:
                    flight_elements = elements
                    print(f"Found {count} flights using selector: {selector}")
                    break
            
            if flight_elements:
                # Limit to top 5 flights
                max_flights = min(5, await flight_elements.count())
                
                for i in range(max_flights):
                    try:
                        flight_element = flight_elements.nth(i)
                        
                        # Extract flight details
                        flight_info = {
                            'rank': i + 1,
                            'airline': 'N/A',
                            'departure_time': 'N/A',
                            'arrival_time': 'N/A',
                            'duration': 'N/A',
                            'stops': 'N/A',
                            'price': 'N/A'
                        }
                        
                        # Try to extract airline
                        airline_selectors = ['img[alt]', '.airline-name', '[data-testid="airline"]', 'span:has-text("Airlines")']
                        for selector in airline_selectors:
                            try:
                                airline_element = flight_element.locator(selector).first
                                if await airline_element.is_visible(timeout=1000):
                                    airline_text = await airline_element.get_attribute('alt') or await airline_element.text_content()
                                    if airline_text and airline_text.strip():
                                        flight_info['airline'] = airline_text.strip()
                                        break
                            except:
                                continue
                        
                        # Try to extract times
                        time_selectors = ['span[aria-label*="Depart"]', 'span[aria-label*="Arrive"]', '.time', '[data-testid="time"]']
                        times = []
                        for selector in time_selectors:
                            try:
                                time_elements = flight_element.locator(selector)
                                count = await time_elements.count()
                                for j in range(min(2, count)):
                                    time_text = await time_elements.nth(j).text_content()
                                    if time_text and time_text.strip():
                                        times.append(time_text.strip())
                            except:
                                continue
                        
                        if len(times) >= 2:
                            flight_info['departure_time'] = times[0]
                            flight_info['arrival_time'] = times[1]
                        
                        # Try to extract duration
                        duration_selectors = ['span[aria-label*="Total duration"]', '.duration', '[data-testid="duration"]']
                        for selector in duration_selectors:
                            try:
                                duration_element = flight_element.locator(selector).first
                                if await duration_element.is_visible(timeout=1000):
                                    duration_text = await duration_element.text_content()
                                    if duration_text and duration_text.strip():
                                        flight_info['duration'] = duration_text.strip()
                                        break
                            except:
                                continue
                        
                        # Try to extract stops
                        stops_selectors = ['span[aria-label*="stop"]', '.stops', '[data-testid="stops"]']
                        for selector in stops_selectors:
                            try:
                                stops_element = flight_element.locator(selector).first
                                if await stops_element.is_visible(timeout=1000):
                                    stops_text = await stops_element.text_content()
                                    if stops_text and stops_text.strip():
                                        flight_info['stops'] = stops_text.strip()
                                        break
                            except:
                                continue
                        
                        # Try to extract price
                        price_selectors = ['span[aria-label*="price"]', '.price', '[data-testid="price"]', 'span:has-text("$")']
                        for selector in price_selectors:
                            try:
                                price_element = flight_element.locator(selector).first
                                if await price_element.is_visible(timeout=1000):
                                    price_text = await price_element.text_content()
                                    if price_text and '$' in price_text:
                                        flight_info['price'] = price_text.strip()
                                        break
                            except:
                                continue
                        
                        flights.append(flight_info)
                        
                    except Exception as e:
                        print(f"Error extracting flight {i+1}: {e}")
                        continue
            
            else:
                print("No flight elements found. The page structure might have changed.")
                # Take a screenshot for debugging
                await page.screenshot(path='debug_screenshot.png')
            
            return flights
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            # Take a screenshot for debugging
            await page.screenshot(path='error_screenshot.png')
            return []
            
        finally:
            await browser.close()

async def main():
    """Main function to run the flight scraper"""
    print("Starting Google Flights scraper...")
    print(f"Searching for flights from SFO to Tokyo")
    print(f"Departure: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Return: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}")
    print("-" * 50)
    
    flights = await scrape_google_flights()
    
    if flights:
        print("\nTop 5 Flights (JSON):")
        print(json.dumps(flights, indent=2, ensure_ascii=False))
    else:
        print("No flights found or error occurred during scraping.")
        print("Check debug_screenshot.png or error_screenshot.png for more details.")

if __name__ == "__main__":
    asyncio.run(main())