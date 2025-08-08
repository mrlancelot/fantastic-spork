#!/usr/bin/env python3
"""
Quick API Test - Test each endpoint with timeout
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # 30 second timeout per request

class QuickTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
    
    def test(self, name: str, method: str, endpoint: str, data=None, params=None):
        """Test a single endpoint with timeout"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                # For GET requests, data becomes params
                response = self.session.get(url, params=data or params, timeout=TIMEOUT)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=TIMEOUT)
            else:
                response = self.session.request(method, url, json=data, params=params, timeout=TIMEOUT)
            
            status = response.status_code
            if status == 200:
                print(f"{Fore.GREEN}✓ {name}: {method} {endpoint} - SUCCESS ({status})")
                self.results.append({"name": name, "status": "success", "code": status})
            else:
                error = response.text[:100] if response.text else "No error message"
                print(f"{Fore.RED}✗ {name}: {method} {endpoint} - FAILED ({status})")
                print(f"  {Fore.YELLOW}Error: {error}")
                self.results.append({"name": name, "status": "failed", "code": status, "error": error})
        except requests.Timeout:
            print(f"{Fore.YELLOW}⚠ {name}: {method} {endpoint} - TIMEOUT ({TIMEOUT}s)")
            self.results.append({"name": name, "status": "timeout"})
        except Exception as e:
            print(f"{Fore.RED}✗ {name}: {method} {endpoint} - ERROR")
            print(f"  {Fore.YELLOW}Error: {str(e)[:100]}")
            self.results.append({"name": name, "status": "error", "error": str(e)})
    
    def run_all(self):
        """Run all tests"""
        print(f"{Fore.CYAN}Quick API Test Suite")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"Target: {BASE_URL}")
        print(f"Timeout: {TIMEOUT}s per request (waiting for responses)")
        print()
        
        # Health
        print(f"{Fore.CYAN}HEALTH Endpoints:")
        self.test("Health Check", "GET", "/api/health")
        self.test("Status", "GET", "/api/status")
        print()
        
        # Flights
        print(f"{Fore.CYAN}FLIGHTS Endpoints:")
        tomorrow = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        self.test("Flight Search", "POST", "/api/flights/search", {
            "origin": "NYC",
            "destination": "LAX",
            "departure_date": tomorrow,
            "adults": 1
        })
        
        self.test("Flexible Search", "POST", "/api/flights/flexible", {
            "origin": "NYC",
            "destination": "LON",
            "departure_month": tomorrow[:7],  # Fixed: use departure_month
            "trip_length_days": 7,
            "adults": 1
        })
        
        self.test("Cheapest Dates", "POST", "/api/flights/cheapest-dates", {
            "origin": "NYC",
            "destination": "PAR"
        })
        
        self.test("Flight Status", "GET", "/api/flights/status", {
            "carrier_code": "AA",
            "flight_number": "100",
            "scheduled_departure_date": tomorrow
        })
        
        self.test("Check-in Links", "GET", "/api/flights/checkin-links", {
            "airline_code": "AA"
        })
        print()
        
        # Hotels
        print(f"{Fore.CYAN}HOTELS Endpoints:")
        check_in = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=63)).strftime("%Y-%m-%d")
        
        self.test("Hotel Search POST", "POST", "/api/hotels/search", {
            "city_code": "PAR",
            "check_in_date": check_in,
            "check_out_date": check_out
        })
        
        self.test("Hotel Search GET", "GET", "/api/hotels/search", {
            "city_code": "NYC",
            "check_in_date": check_in,
            "check_out_date": check_out
        })
        
        self.test("Hotel Sentiments", "POST", "/api/hotels/sentiments", {
            "hotel_ids": ["MCLONGHM"]
        })
        print()
        
        # Activities
        print(f"{Fore.CYAN}ACTIVITIES Endpoints:")
        self.test("Activities Search POST", "POST", "/api/activities/search", {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "radius": 5
        })
        
        self.test("Activities Search GET", "GET", "/api/activities/search", {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 5
        })
        print()
        
        # Analytics
        print(f"{Fore.CYAN}ANALYTICS Endpoints:")
        self.test("Flight Inspiration", "GET", "/api/analytics/flight-inspiration", {
            "origin": "NYC"
        })
        
        self.test("Most Traveled", "GET", "/api/analytics/most-traveled", {
            "origin_city_code": "NYC",
            "period": "2024-01"
        })
        
        self.test("Most Booked", "GET", "/api/analytics/most-booked", {
            "origin_city_code": "PAR",
            "period": "2024-01"
        })
        
        self.test("Busiest Period", "GET", "/api/analytics/busiest-period", {
            "city_code": "NYC",
            "period": "2024",
            "direction": "ARRIVING"
        })
        
        self.test("Flight Delay Prediction", "POST", "/api/analytics/flight-delay-prediction", {
            "origin_airport": "JFK",
            "destination_airport": "LAX",
            "departure_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "departure_time": "14:00",
            "arrival_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "arrival_time": "17:00",
            "airline_code": "AA",
            "flight_number": "100",
            "aircraft_code": "738"
        })
        
        self.test("Trip Purpose", "POST", "/api/analytics/trip-purpose-prediction", {
            "origin_airport": "NYC",
            "destination_airport": "SFO",
            "departure_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "return_date": (datetime.now() + timedelta(days=67)).strftime("%Y-%m-%d"),
            "search_date": datetime.now().strftime("%Y-%m-%d")
        })
        
        self.test("Airport Routes", "GET", "/api/analytics/airport-routes", {
            "airport_code": "JFK"
        })
        
        self.test("Price Analysis", "POST", "/api/analytics/price-analysis", {
            "origin": "NYC",
            "destination": "LON",
            "departure_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        })
        print()
        
        # Planner
        print(f"{Fore.CYAN}PLANNER Endpoints:")
        self.test("Smart Itinerary", "POST", "/api/planner/smart", {
            "destination": "Paris, France",
            "start_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=65)).strftime("%Y-%m-%d"),
            "interests": ["art", "food"],
            "budget": 2000
        })
        
        self.test("Save Itinerary", "POST", "/api/planner/save", {
            "title": "Test Trip",
            "destination": "Paris",
            "start_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=65)).strftime("%Y-%m-%d"),
            "itinerary": {}
        })
        print()
        
        # Chat
        print(f"{Fore.CYAN}AI CHAT Endpoints:")
        self.test("Chat", "POST", "/api/chat/", {
            "message": "What are the best places to visit in Tokyo?"
        })
        
        self.test("Agent Chat", "POST", "/api/chat/agent", {
            "message": "Find flights from NYC to Paris"
        })
        print()
        
        # Summary
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}SUMMARY")
        print(f"{Fore.CYAN}{'='*60}")
        
        success = sum(1 for r in self.results if r.get("status") == "success")
        failed = sum(1 for r in self.results if r.get("status") == "failed")
        timeout = sum(1 for r in self.results if r.get("status") == "timeout")
        error = sum(1 for r in self.results if r.get("status") == "error")
        total = len(self.results)
        
        print(f"{Fore.GREEN}✓ Success: {success}/{total}")
        print(f"{Fore.RED}✗ Failed: {failed}/{total}")
        print(f"{Fore.YELLOW}⚠ Timeout: {timeout}/{total}")
        print(f"{Fore.RED}⚠ Error: {error}/{total}")
        
        success_rate = (success / total * 100) if total > 0 else 0
        print(f"\n{Fore.CYAN}Success Rate: {success_rate:.1f}%")
        
        # Save results
        with open("test_api/quick_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "success": success,
                    "failed": failed,
                    "timeout": timeout,
                    "error": error,
                    "success_rate": success_rate
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n{Fore.CYAN}Detailed results saved to test_api/quick_results.json")

if __name__ == "__main__":
    tester = QuickTester()
    tester.run_all()