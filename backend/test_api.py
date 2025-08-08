"""Test the agent API endpoint"""

import asyncio
import aiohttp
import json

async def test_agent_api():
    """Test the agent planning API"""
    
    url = "http://localhost:8000/api/agent/plan"
    
    request_data = {
        "destination": "Tokyo",
        "start_date": "2025-03-01",
        "end_date": "2025-03-07",
        "origin": "New York",
        "budget": 5000,
        "travelers": 2,
        "interests": ["food", "culture"]
    }
    
    print(f"Testing API: {url}")
    print(f"Request: {json.dumps(request_data, indent=2)}")
    print("\n=== Streaming Response ===\n")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request_data) as response:
            if response.status == 200:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            print("\n=== Stream Complete ===")
                            break
                        try:
                            thought = json.loads(data)
                            print(f"[{thought['action'].upper()}] {thought['content'][:100]}...")
                        except json.JSONDecodeError:
                            pass
            else:
                error = await response.text()
                print(f"Error {response.status}: {error}")

if __name__ == "__main__":
    asyncio.run(test_agent_api())