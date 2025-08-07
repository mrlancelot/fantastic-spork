"""Workflow Agent - Clean orchestration of complex travel planning workflows

Handles:
- Query intent analysis
- Multi-step travel planning workflows
- Integration between AI agent and travel services
- Complex travel planning scenarios
"""

import asyncio
from typing import Dict, Any, List, Optional
from ..core.config import get_settings
from ..agents.ai_agent import AIAgent
# Travel services imported separately

class WorkflowAgent:
    """Clean workflow agent for complex travel planning"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_agent = AIAgent()
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a travel planning query through the workflow"""
        try:
            # Analyze the query to determine intent
            intent = self._analyze_query_intent(query)
            
            # Route to appropriate workflow based on intent
            if intent["type"] == "flight_search":
                return await self._handle_flight_search(query, intent, context)
            elif intent["type"] == "hotel_search":
                return await self._handle_hotel_search(query, intent, context)
            elif intent["type"] == "restaurant_search":
                return await self._handle_restaurant_search(query, intent, context)
            elif intent["type"] == "general_planning":
                return await self._handle_general_planning(query, context)
            else:
                return await self._handle_general_chat(query, context)
        
        except Exception as e:
            return {
                "response": f"I'm here to help with your travel planning! Could you tell me more about what you're looking for?",
                "error": str(e),
                "fallback": True
            }
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and extract parameters"""
        query_lower = query.lower()
        
        # Flight search intent
        if any(word in query_lower for word in ["flight", "fly", "airline", "airport", "departure", "arrival"]):
            return {
                "type": "flight_search",
                "confidence": 0.8,
                "entities": self._extract_travel_entities(query)
            }
        
        # Hotel search intent
        elif any(word in query_lower for word in ["hotel", "accommodation", "stay", "room", "booking"]):
            return {
                "type": "hotel_search",
                "confidence": 0.8,
                "entities": self._extract_travel_entities(query)
            }
        
        # Restaurant search intent
        elif any(word in query_lower for word in ["restaurant", "food", "eat", "dining", "cuisine"]):
            return {
                "type": "restaurant_search",
                "confidence": 0.7,
                "entities": self._extract_travel_entities(query)
            }
        
        # General travel planning
        elif any(word in query_lower for word in ["trip", "travel", "vacation", "itinerary", "plan"]):
            return {
                "type": "general_planning",
                "confidence": 0.6,
                "entities": self._extract_travel_entities(query)
            }
        
        else:
            return {
                "type": "general_chat",
                "confidence": 0.3,
                "entities": {}
            }
    
    def _extract_travel_entities(self, query: str) -> Dict[str, Any]:
        """Extract travel-related entities from query (simplified implementation)"""
        entities = {
            "destinations": [],
            "dates": [],
            "preferences": []
        }
        
        # Common destination keywords (simplified for MVP)
        destinations = [
            "tokyo", "paris", "london", "new york", "singapore", "bangkok",
            "rome", "barcelona", "amsterdam", "sydney", "dubai", "istanbul",
            "lisbon", "prague", "vienna", "berlin", "madrid", "milan"
        ]
        
        for dest in destinations:
            if dest in query.lower():
                entities["destinations"].append(dest.title())
        
        # Basic date pattern matching (simplified)
        import re
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',   # YYYY-MM-DD
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query.lower())
            entities["dates"].extend(matches)
        
        return entities
    
    async def _handle_flight_search(self, query: str, intent: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle flight search workflow"""
        try:
            entities = intent.get("entities", {})
            destinations = entities.get("destinations", [])
            
            if len(destinations) >= 2:
                # We have origin and destination
                origin = destinations[0]
                destination = destinations[1]
                
                response = f"I can help you search for flights from {origin} to {destination}. What dates are you considering?"
                
                return {
                    "response": response,
                    "action": "flight_search",
                    "parameters": {"origin": origin, "destination": destination},
                    "next_step": "Provide your preferred travel dates to see flight options."
                }
            else:
                return {
                    "response": "I'd be happy to help you find flights! Could you tell me your departure and destination cities?",
                    "action": "flight_search_input_needed"
                }
        
        except Exception as e:
            return {
                "response": "I can help you search for flights. Please let me know your travel cities and preferred dates.",
                "fallback": True
            }
    
    async def _handle_hotel_search(self, query: str, intent: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle hotel search workflow"""
        entities = intent.get("entities", {})
        destinations = entities.get("destinations", [])
        
        if destinations:
            destination = destinations[0]
            return {
                "response": f"I can help you find hotels in {destination}. What are your check-in and check-out dates?",
                "action": "hotel_search",
                "parameters": {"destination": destination},
                "next_step": "Provide your check-in and check-out dates to see hotel options."
            }
        else:
            return {
                "response": "I'd be happy to help you find accommodation! Which city or area are you looking to stay in?",
                "action": "hotel_search_input_needed"
            }
    
    async def _handle_restaurant_search(self, query: str, intent: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle restaurant search workflow"""
        entities = intent.get("entities", {})
        destinations = entities.get("destinations", [])
        
        if destinations:
            destination = destinations[0]
            try:
                restaurant_results = await self.ai_agent.search_restaurants(query, destination)
                return {
                    "response": f"Here are some great restaurant recommendations for {destination}!",
                    "data": restaurant_results,
                    "action": "restaurant_search"
                }
            except Exception as e:
                return {
                    "response": f"I can help you find great restaurants in {destination}. What type of cuisine are you interested in?",
                    "action": "restaurant_search_fallback"
                }
        else:
            return {
                "response": "I'd love to help you find great restaurants! Which city are you visiting?",
                "action": "restaurant_search_input_needed"
            }
    
    async def _handle_general_planning(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle general travel planning queries"""
        try:
            # Use AI agent for general travel recommendations
            response = await self.ai_agent.chat_completion(query, context)
            suggestions = await self.ai_agent.generate_smart_suggestions(context or {})
            
            return {
                "response": response,
                "action": "general_planning",
                "suggestions": suggestions
            }
        except Exception as e:
            return {
                "response": "I'm here to help you plan an amazing trip! What kind of experience are you looking for?",
                "fallback": True
            }
    
    async def _handle_general_chat(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle general chat and travel advice"""
        try:
            response = await self.ai_agent.chat_completion(query, context)
            return {
                "response": response,
                "action": "general_chat"
            }
        except Exception as e:
            return {
                "response": "I'm your travel planning assistant! I can help you find flights, hotels, restaurants, and plan amazing itineraries. What would you like to explore?",
                "fallback": True
            }
    
    async def multi_step_planning(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multi-step travel planning workflows"""
        try:
            results = {}
            
            # Step 1: Flight search if requested
            if requirements.get("flights"):
                flight_data = requirements["flights"]
                from models.requests import FlightSearchRequest
                flight_request = FlightSearchRequest(**flight_data)
                results["flights"] = await self.travel_service.search_flights(flight_request)
            
            # Step 2: Hotel search if requested  
            if requirements.get("hotels"):
                hotel_data = requirements["hotels"]
                from models.requests import HotelSearchRequest
                hotel_request = HotelSearchRequest(**hotel_data)
                results["hotels"] = await self.travel_service.search_hotels(hotel_request)
            
            # Step 3: Restaurant recommendations
            if requirements.get("restaurants"):
                location = requirements["restaurants"].get("location")
                cuisine = requirements["restaurants"].get("cuisine", "local cuisine")
                results["restaurants"] = await self.ai_agent.search_restaurants(cuisine, location)
            
            # Step 4: Generate summary
            summary = self._generate_planning_summary(results, requirements)
            
            return {
                "results": results,
                "summary": summary,
                "status": "completed"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "message": "Multi-step planning encountered an error"
            }
    
    def _generate_planning_summary(self, results: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Generate a summary of the planning results"""
        try:
            destination = requirements.get("destination", "your destination")
            
            summary_parts = [f"Here's your travel plan for {destination}:"]
            
            if "flights" in results and results["flights"].get("data"):
                flight_count = len(results["flights"]["data"])
                summary_parts.append(f"✈️ Found {flight_count} flight options")
            
            if "hotels" in results and results["hotels"].get("data"):
                hotel_count = len(results["hotels"]["data"])
                summary_parts.append(f"🏨 Found {hotel_count} hotel options")
            
            if "restaurants" in results:
                summary_parts.append(f"🍽️ Restaurant recommendations included")
            
            summary_parts.append("\nEverything is ready for your amazing trip!")
            
            return " ".join(summary_parts)
        
        except Exception as e:
            return "Your travel planning is complete! Check the details above."
