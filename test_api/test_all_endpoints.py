#!/usr/bin/env python3
"""
Comprehensive API Test Suite for TravelAI Backend
Tests all endpoints documented in the API specification
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, category: str, endpoint: str, method: str, status: str, details: str = ""):
        """Log test result"""
        color = Fore.GREEN if status == "SUCCESS" else Fore.RED if status == "FAILED" else Fore.YELLOW
        print(f"{color}[{category}] {method} {endpoint}: {status} {details}")
        self.results.append({
            "category": category,
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details
        })
    
    def test_endpoint(self, category: str, endpoint: str, method: str = "GET", 
                     data: Dict = None, params: Dict = None) -> Dict:
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            else:
                response = self.session.request(method, url, json=data, params=params)
            
            if response.status_code == 200:
                self.log_result(category, endpoint, method, "SUCCESS", f"Status: {response.status_code}")
                return {"success": True, "data": response.json()}
            else:
                self.log_result(category, endpoint, method, "FAILED", 
                              f"Status: {response.status_code} - {response.text[:100]}")
                return {"success": False, "error": response.text}
        except Exception as e:
            self.log_result(category, endpoint, method, "ERROR", str(e)[:100])
            return {"success": False, "error": str(e)}
    
    def test_health_endpoints(self):
        """Test Health Check endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing HEALTH endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        self.test_endpoint("Health", "/api/health", "GET")
        self.test_endpoint("Health", "/api/status", "GET")
    
    def test_flight_endpoints(self):
        """Test Flight endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing FLIGHTS endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Search flights
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        flight_search = {
            "origin": "NYC",
            "destination": "LAX",
            "departure_date": tomorrow,
            "adults": 1,
            "travel_class": "ECONOMY",
            "max_results": 5
        }
        self.test_endpoint("Flights", "/api/flights/search", "POST", flight_search)
        
        # Flexible dates search
        flexible_search = {
            "origin": "NYC",
            "destination": "LON",
            "departure_date": tomorrow,
            "duration": 7,
            "adults": 1
        }
        self.test_endpoint("Flights", "/api/flights/flexible", "POST", flexible_search)
        
        # Cheapest dates
        cheapest_dates = {
            "origin": "NYC",
            "destination": "PAR"
        }
        self.test_endpoint("Flights", "/api/flights/cheapest-dates", "POST", cheapest_dates)
        
        # Flight status
        params = {
            "carrier_code": "AA",
            "flight_number": "100",
            "scheduled_departure_date": tomorrow
        }
        self.test_endpoint("Flights", "/api/flights/status", "GET", params=params)
        
        # Check-in links
        params = {"airline_code": "AA"}
        self.test_endpoint("Flights", "/api/flights/checkin-links", "GET", params=params)
    
    def test_hotel_endpoints(self):
        """Test Hotel endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing HOTELS endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Search hotels
        check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=33)).strftime("%Y-%m-%d")
        
        hotel_search = {
            "city_code": "PAR",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": 2,
            "radius": 5,
            "radius_unit": "KM",
            "price_range": "100-500",
            "currency": "USD",
            "ratings": [4, 5]
        }
        self.test_endpoint("Hotels", "/api/hotels/search", "POST", hotel_search)
        
        # GET method for hotel search
        params = {
            "city_code": "NYC",
            "check_in_date": check_in,
            "check_out_date": check_out
        }
        self.test_endpoint("Hotels", "/api/hotels/search", "GET", params=params)
        
        # Hotel sentiments
        sentiments_request = {
            "hotel_ids": ["MCLONGHM", "MCNYCMIM"]
        }
        self.test_endpoint("Hotels", "/api/hotels/sentiments", "POST", sentiments_request)
    
    def test_activities_endpoints(self):
        """Test Activities endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing ACTIVITIES endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Search activities - POST
        activities_search = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "radius": 5,
            "max_results": 10
        }
        self.test_endpoint("Activities", "/api/activities/search", "POST", activities_search)
        
        # Search activities - GET
        params = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 5
        }
        self.test_endpoint("Activities", "/api/activities/search", "GET", params=params)
    
    def test_analytics_endpoints(self):
        """Test Analytics endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing ANALYTICS endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Flight inspiration
        params = {"origin": "NYC"}
        self.test_endpoint("Analytics", "/api/analytics/flight-inspiration", "GET", params=params)
        
        # Most traveled destinations
        params = {"origin_city_code": "NYC", "period": "2024-01"}
        self.test_endpoint("Analytics", "/api/analytics/most-traveled", "GET", params=params)
        
        # Most booked destinations
        params = {"origin_city_code": "PAR", "period": "2024-01"}
        self.test_endpoint("Analytics", "/api/analytics/most-booked", "GET", params=params)
        
        # Busiest period
        params = {"city_code": "NYC", "period": "2024", "direction": "ARRIVING"}
        self.test_endpoint("Analytics", "/api/analytics/busiest-period", "GET", params=params)
        
        # Flight delay prediction
        delay_request = {
            "origin_airport": "JFK",
            "destination_airport": "LAX",
            "departure_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "departure_time": "14:00",
            "arrival_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "arrival_time": "17:00",
            "airline_code": "AA",
            "flight_number": "100",
            "aircraft_code": "738"
        }
        self.test_endpoint("Analytics", "/api/analytics/flight-delay-prediction", "POST", delay_request)
        
        # Trip purpose prediction
        purpose_request = {
            "origin_airport": "NYC",
            "destination_airport": "SFO",
            "departure_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "return_date": (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d"),
            "search_date": datetime.now().strftime("%Y-%m-%d")
        }
        self.test_endpoint("Analytics", "/api/analytics/trip-purpose-prediction", "POST", purpose_request)
        
        # Airport routes
        params = {"airport_code": "JFK", "max_results": 10}
        self.test_endpoint("Analytics", "/api/analytics/airport-routes", "GET", params=params)
        
        # Price analysis
        price_analysis = {
            "origin": "NYC",
            "destination": "LON",
            "departure_date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "one_way": False,
            "duration": 7,
            "all_combinations": True,
            "max_price": 1000,
            "view_by": "WEEK"
        }
        self.test_endpoint("Analytics", "/api/analytics/price-analysis", "POST", price_analysis)
    
    def test_planner_endpoints(self):
        """Test Planner endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing PLANNER endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Smart itinerary
        planner_request = {
            "destination": "Paris, France",
            "arrival_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "departure_date": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d"),
            "interests": ["art", "food", "history"],
            "budget": "moderate",
            "pace": "relaxed",
            "accommodation_type": "hotel",
            "dietary_restrictions": ["vegetarian"]
        }
        self.test_endpoint("Planner", "/api/planner/smart", "POST", planner_request)
        
        # Save itinerary (would need valid data)
        save_request = {
            "title": "Test Trip to Paris",
            "destination": "Paris",
            "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d"),
            "itinerary": {},
            "metadata": {"created_by": "test"}
        }
        self.test_endpoint("Planner", "/api/planner/save", "POST", save_request)
        
        # Update slot (example)
        date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.test_endpoint("Planner", f"/api/planner/slot/{date}/morning", "PUT", {})
        
        # Complete slot
        complete_request = {
            "date": date,
            "slot_id": "morning",
            "completed": True
        }
        self.test_endpoint("Planner", "/api/planner/slot/complete", "POST", complete_request)
    
    def test_chat_endpoints(self):
        """Test AI Chat endpoints"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing AI CHAT endpoints")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Basic chat
        chat_request = {
            "message": "What are the best places to visit in Tokyo?",
            "context": {}
        }
        self.test_endpoint("AI Chat", "/api/chat/", "POST", chat_request)
        
        # Agent chat
        agent_request = {
            "message": "Find me flights from New York to Paris next month",
            "context": {"user_preferences": {"budget": "moderate"}}
        }
        self.test_endpoint("AI Chat", "/api/chat/agent", "POST", agent_request)
    
    def generate_summary(self):
        """Generate test summary"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}TEST SUMMARY")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Count results by status
        success = sum(1 for r in self.results if r["status"] == "SUCCESS")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        total = len(self.results)
        
        # Group by category
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"success": 0, "failed": 0, "error": 0}
            
            if result["status"] == "SUCCESS":
                categories[cat]["success"] += 1
            elif result["status"] == "FAILED":
                categories[cat]["failed"] += 1
            else:
                categories[cat]["error"] += 1
        
        # Print category breakdown
        print(f"{Fore.WHITE}Category Breakdown:")
        print(f"{Fore.WHITE}{'-'*40}")
        for cat, stats in categories.items():
            total_cat = stats["success"] + stats["failed"] + stats["error"]
            success_rate = (stats["success"] / total_cat * 100) if total_cat > 0 else 0
            color = Fore.GREEN if success_rate >= 80 else Fore.YELLOW if success_rate >= 50 else Fore.RED
            print(f"{color}{cat:15} | ✓ {stats['success']:2} | ✗ {stats['failed']:2} | ⚠ {stats['error']:2} | {success_rate:.0f}%")
        
        # Overall summary
        print(f"\n{Fore.WHITE}Overall Results:")
        print(f"{Fore.WHITE}{'-'*40}")
        success_rate = (success / total * 100) if total > 0 else 0
        
        print(f"{Fore.GREEN}✓ Successful: {success}/{total}")
        print(f"{Fore.RED}✗ Failed:     {failed}/{total}")
        print(f"{Fore.YELLOW}⚠ Errors:     {errors}/{total}")
        print(f"\n{Fore.CYAN}Success Rate: {success_rate:.1f}%")
        
        # List all failed endpoints
        if failed > 0 or errors > 0:
            print(f"\n{Fore.RED}Failed/Error Endpoints:")
            print(f"{Fore.RED}{'-'*40}")
            for result in self.results:
                if result["status"] in ["FAILED", "ERROR"]:
                    print(f"{Fore.RED}• {result['method']} {result['endpoint']}")
                    print(f"  {result['details'][:80]}")
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "errors": errors,
            "success_rate": success_rate,
            "categories": categories
        }
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print(f"{Fore.CYAN}Starting Comprehensive API Testing")
        print(f"{Fore.CYAN}Target: {BASE_URL}")
        print(f"{Fore.CYAN}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_health_endpoints()
        self.test_flight_endpoints()
        self.test_hotel_endpoints()
        self.test_activities_endpoints()
        self.test_analytics_endpoints()
        self.test_planner_endpoints()
        self.test_chat_endpoints()
        
        summary = self.generate_summary()
        
        # Save results to file
        with open("test_api/test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "detailed_results": self.results
            }, f, indent=2)
        
        print(f"\n{Fore.CYAN}Results saved to test_api/test_results.json")
        
        return summary

if __name__ == "__main__":
    tester = APITester()
    summary = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if summary["failed"] > 0 or summary["errors"] > 0:
        sys.exit(1)