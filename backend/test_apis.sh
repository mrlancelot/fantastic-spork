#!/bin/bash

# TravelAI Backend API Test Script
# Tests all endpoints with real Amadeus data

API_BASE="http://localhost:8000/api"

echo "================================================"
echo "TravelAI Backend API Test Suite"
echo "================================================"
echo ""

# 1. Health Check
echo "1. HEALTH CHECK"
echo "----------------"
curl -s "$API_BASE/health" | jq .
echo ""

# 2. Status Check
echo "2. STATUS CHECK"
echo "----------------"
curl -s "$API_BASE/status" | jq .
echo ""

# 3. Flight Search (NYC to LAX)
echo "3. FLIGHT SEARCH (NYC -> LAX)"
echo "------------------------------"
curl -s -X POST "$API_BASE/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "NYC",
    "destination": "LAX",
    "departure_date": "2025-03-15",
    "adults": 1,
    "trip_type": "one-way",
    "seat_class": "economy"
  }' | jq '.status, .error // .data.total_flights'
echo ""

# 4. Hotel Search (Paris)
echo "4. HOTEL SEARCH (Paris)"
echo "------------------------"
curl -s -X POST "$API_BASE/hotels/search" \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "PAR",
    "check_in_date": "2025-03-15",
    "check_out_date": "2025-03-18",
    "adults": 2,
    "rooms": 1
  }' | jq '.status, .error // .data.total_hotels'
echo ""

# 5. Activities Search (Paris)
echo "5. ACTIVITIES SEARCH (Paris)"
echo "-----------------------------"
curl -s -X POST "$API_BASE/activities/search" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 48.8566,
    "longitude": 2.3522,
    "radius": 5,
    "adults": 2
  }' | jq '.status, .data.total_activities'
echo ""

# 6. Flight Status
echo "6. FLIGHT STATUS (AA100)"
echo "-------------------------"
curl -s "$API_BASE/flights/status?carrier_code=AA&flight_number=100&scheduled_departure_date=2025-03-15" \
  | jq '.status, .error // .data.flight.status'
echo ""

# 7. Check-in Links
echo "7. CHECK-IN LINKS (American Airlines)"
echo "--------------------------------------"
curl -s "$API_BASE/flights/checkin-links?airline_code=AA" \
  | jq '.status, .data.airline.check_in_url // .error'
echo ""

# 8. Flight Inspiration
echo "8. FLIGHT INSPIRATION (NYC, $500 budget)"
echo "-----------------------------------------"
curl -s "$API_BASE/analytics/flight-inspiration?origin=NYC&max_price=500" \
  | jq '.status, .data.total_found // .error'
echo ""

# 9. Most Traveled Destinations
echo "9. MOST TRAVELED FROM NYC"
echo "--------------------------"
curl -s "$API_BASE/analytics/most-traveled?origin_city_code=NYC&period=2025-02" \
  | jq '.status, .error // .data'
echo ""

# 10. Airport Routes
echo "10. AIRPORT ROUTES (JFK)"
echo "-------------------------"
curl -s "$API_BASE/analytics/airport-routes?airport_code=JFK" \
  | jq '.status, .error // .data'
echo ""

# 11. Smart Planner
echo "11. SMART PLANNER (Paris Trip)"
echo "-------------------------------"
curl -s -X POST "$API_BASE/planner/smart" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2025-03-15",
    "end_date": "2025-03-18",
    "travelers": 2,
    "preferences": ["culture", "food"],
    "budget": 5000
  }' | jq '.status, .data.days_planned'
echo ""

# 12. AI Chat
echo "12. AI CHAT"
echo "------------"
curl -s -X POST "$API_BASE/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best restaurants in Paris?",
    "context": null
  }' | jq '.status, .response | .[0:100]'
echo ""

echo "================================================"
echo "API Test Suite Complete"
echo "================================================"