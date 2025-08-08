"""Minimal Day Planner Agent - Uses AI thinking to create unique daily plans"""

import json
import aiohttp
import os
from typing import Dict, List, Any

TOKYO_KNOWLEDGE = """
Major Attractions:
- Morning: Senso-ji Temple, Meiji Shrine, Imperial Palace, Tsukiji Outer Market, Tokyo Tower, Ueno Park
- Cultural: teamLab Borderless, Edo-Tokyo Museum, National Museum, Ghibli Museum, Samurai Museum
- Districts: Shibuya, Harajuku, Asakusa, Ginza, Akihabara, Roppongi, Odaiba, Shinjuku, Ikebukuro

Cuisine Types:
sushi, ramen, tempura, yakitori, kaiseki, tonkatsu, udon, soba, okonomiyaki, wagyu, 
izakaya, teppanyaki, unagi, curry, donburi, takoyaki, kushikatsu, shabu-shabu

Unique Experiences:
Robot Restaurant, Tokyo Skytree, Sumo practice, Onsen, Karaoke, Maid Cafe, 
Go-karting, Cooking class, Tea ceremony, Calligraphy, Origami workshop
"""

class DayPlannerAgent:
    """Minimal agent that uses AI to plan unique days"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.llm_url = "https://openrouter.ai/api/v1/chat/completions"
    
    async def plan_day(self, destination: str, day_num: int, total_days: int, 
                       previous_activities: List[str], interests: List[str]) -> Dict[str, Any]:
        """Generate unique activities for a specific day"""
        
        prompt = f"""
        <think>
        Planning day {day_num} of {total_days} in {destination}.
        Previous activities done: {json.dumps(previous_activities) if previous_activities else "None"}
        User interests: {', '.join(interests)}
        
        Must create 4 DIFFERENT activities that:
        1. Don't repeat any previous restaurants or attractions
        2. Focus on a specific area/district to minimize travel
        3. Match the day's energy (early days=high energy, later=relaxed)
        4. Include actual restaurant names where possible
        
        {TOKYO_KNOWLEDGE}
        </think>
        
        Generate day {day_num} activities. Return ONLY a JSON object:
        {{
            "morning": "Specific attraction name and brief description",
            "lunch": "Restaurant name and cuisine type",
            "afternoon": "Activity or district exploration", 
            "dinner": "Different restaurant and cuisine"
        }}
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "z-ai/glm-4.5",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.llm_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    # Parse JSON from response
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0]
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0]
                    return json.loads(content.strip())
                else:
                    error_text = await response.text()
                    raise Exception(f"API error: {response.status} - {error_text}")