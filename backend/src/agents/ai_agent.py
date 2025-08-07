"""AI Agent - Clean LLM integration for travel recommendations

Handles:
- Chat completions with Gemini/OpenAI
- Restaurant search with web scraping
- Travel recommendations
- Smart suggestions based on context
"""

import os
from typing import Optional, Dict, Any, List
from ..core.config import get_settings
from ..core.exceptions import ExternalAPIError

try:
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.google_genai import GoogleGenAI as Gemini
    from llama_index.llms.openai import OpenAI
except ImportError:
    FunctionAgent = None
    Gemini = None
    OpenAI = None

class AIAgent:
    """Clean AI agent for LLM-powered travel tasks"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._get_llm()
    
    def _get_llm(self) -> Optional[Any]:
        """Get the appropriate LLM instance based on available API keys"""
        if not (Gemini or OpenAI):
            return None
            
        try:
            # Prefer OpenRouter if available
            if OpenAI and self.settings.openrouter_api_key:
                return OpenAI(
                    model="openai/gpt-4o-mini",
                    api_key=self.settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.3
                )
            
            # Fallback to Google Gemini
            if Gemini and self.settings.gemini_api_key:
                return Gemini(
                    model="models/gemini-1.5-pro",
                    api_key=self.settings.gemini_api_key
                )
        except Exception as e:
            print(f"Failed to initialize LLM: {e}")
        
        return None
    
    async def chat_completion(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Basic chat completion for travel-related queries"""
        try:
            if not self.llm:
                return f"I understand you're asking about: {message}. How can I help you plan your trip?"
            
            system_context = ""
            if context:
                system_context = f"Context: {context}"
            
            prompt = f"""
You are a helpful travel planning assistant. {system_context}

User: {message}

Provide a helpful, informative response about travel planning, destinations, or trip organization.
Keep your response concise and actionable.
"""
            
            response = await self.llm.acomplete(prompt)
            return str(response)
        
        except Exception as e:
            return f"I understand you're asking about: {message}. How can I help you plan your trip?"
    
    async def search_restaurants(self, query: str, location: str) -> Dict[str, Any]:
        """Search for restaurants using AI (fallback to mock data)"""
        try:
            if self.llm:
                prompt = f"""
Find and recommend 3 restaurants for '{query}' in {location}.

Provide:
1. Restaurant name
2. Cuisine type  
3. Price range ($ to $$$$)
4. Rating estimate
5. Brief description
6. Why it matches the query

Format as a JSON-like structure.
"""
                
                response = await self.llm.acomplete(prompt)
                
                return {
                    "result": str(response),
                    "query": query,
                    "location": location,
                    "ai_powered": True
                }
            else:
                # Fallback mock data
                return {
                    "result": [{
                        "name": f"Local Restaurant in {location}",
                        "cuisine": "Local cuisine",
                        "rating": 4.5,
                        "price_range": "$$",
                        "booking_url": "https://opentable.com",
                        "description": f"Great restaurant for {query} in {location}"
                    }],
                    "fallback": True,
                    "query": query,
                    "location": location
                }
                
        except Exception as e:
            return {
                "result": [{
                    "name": f"Recommended Restaurant in {location}",
                    "cuisine": "Local cuisine",
                    "rating": 4.2,
                    "price_range": "$$",
                    "description": f"Great option for {query} in {location}",
                    "booking_url": "https://opentable.com"
                }],
                "fallback": True,
                "error": str(e)
            }
    
    async def generate_travel_recommendations(self, destination: str, preferences: List[str]) -> Dict[str, Any]:
        """Generate AI-powered travel recommendations"""
        try:
            if not self.llm:
                return {
                    "recommendations": f"Here are some great recommendations for {destination} based on your preferences.",
                    "fallback": True
                }
            
            prompt = f"""
Generate travel recommendations for {destination} based on these preferences: {', '.join(preferences)}.

Include:
1. Top 3 must-see attractions
2. 2 recommended restaurants  
3. 1 unique local experience
4. Best time to visit each recommendation
5. Estimated duration for each activity

Format as a structured, actionable response.
"""
            
            response = await self.llm.acomplete(prompt)
            
            return {
                "recommendations": str(response),
                "destination": destination,
                "preferences": preferences,
                "ai_powered": True
            }
        
        except Exception as e:
            return {
                "recommendations": f"Here are some great recommendations for {destination} based on your preferences.",
                "fallback": True,
                "error": str(e)
            }
    
    async def generate_smart_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Generate context-aware suggestions using AI"""
        try:
            if not self.llm:
                return [
                    "Explore local markets",
                    "Try a traditional restaurant",
                    "Visit a popular attraction"
                ]
            
            destination = context.get("destination", "your destination")
            weather = context.get("weather", {})
            time_of_day = context.get("time_of_day", "day")
            user_mood = context.get("mood", "neutral")
            
            prompt = f"""
Generate 3 personalized travel suggestions for someone in {destination}.
Context:
- Weather: {weather.get('condition', 'unknown')}, {weather.get('temperature', 'mild')}
- Time: {time_of_day}
- Mood: {user_mood}

Make suggestions practical, specific, and engaging. 
Keep each suggestion under 50 characters.
Return as a simple list.
"""
            
            response = await self.llm.acomplete(prompt)
            suggestions = str(response).split('\n')[:3]
            
            return [s.strip('- ').strip() for s in suggestions if s.strip()]
        
        except Exception as e:
            # Fallback suggestions
            return [
                "Explore local markets",
                "Try a traditional restaurant",
                "Visit a popular attraction"
            ]
    
    async def analyze_trip_purpose(self, activities: List[str], duration: int) -> Dict[str, Any]:
        """Analyze trip purpose based on activities and duration"""
        try:
            # Simple rule-based analysis (no LLM needed for this)
            business_keywords = ["meeting", "conference", "office", "client", "business"]
            leisure_keywords = ["beach", "museum", "restaurant", "sightseeing", "vacation"]
            adventure_keywords = ["hiking", "climbing", "diving", "safari", "adventure"]
            
            business_score = sum(1 for activity in activities if any(kw in activity.lower() for kw in business_keywords))
            leisure_score = sum(1 for activity in activities if any(kw in activity.lower() for kw in leisure_keywords))
            adventure_score = sum(1 for activity in activities if any(kw in activity.lower() for kw in adventure_keywords))
            
            total_activities = len(activities)
            if total_activities == 0:
                return {
                    "purpose": "unknown",
                    "confidence": 0.0,
                    "recommendations": []
                }
            
            if business_score > leisure_score and business_score > adventure_score:
                purpose = "business"
                confidence = min(0.9, business_score / total_activities + 0.3)
            elif adventure_score > leisure_score:
                purpose = "adventure"
                confidence = min(0.9, adventure_score / total_activities + 0.3)
            else:
                purpose = "leisure"
                confidence = min(0.9, leisure_score / total_activities + 0.3)
            
            recommendations = {
                "business": ["Book airport lounge access", "Consider business hotels", "Schedule buffer time for meetings"],
                "leisure": ["Add cultural activities", "Book scenic restaurants", "Plan relaxation time"],
                "adventure": ["Pack appropriate gear", "Book adventure insurance", "Check weather conditions"]
            }.get(purpose, [])
            
            return {
                "primary_purpose": purpose,
                "confidence": confidence,
                "recommendations": recommendations,
                "analysis": {
                    "business_score": business_score,
                    "leisure_score": leisure_score,
                    "adventure_score": adventure_score
                }
            }
        
        except Exception as e:
            return {
                "primary_purpose": "unknown",
                "confidence": 0.0,
                "recommendations": [],
                "error": str(e)
            }
