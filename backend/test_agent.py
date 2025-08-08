"""Test script for the Master Travel Agent"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env, override=True)

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent))

from src.agents.master_agent import MasterTravelAgent, TripRequest

async def test_agent():
    """Test the master agent functionality"""
    
    # Create agent
    agent = MasterTravelAgent()
    
    # Test 1: Quick search
    print("\n=== Testing Quick Search ===")
    result = await agent.quick_search("What are the best restaurants in Tokyo?")
    print(f"Quick Search Result: {result[:500]}...")
    
    # Test 2: Trip planning (streaming)
    print("\n=== Testing Trip Planning ===")
    request = TripRequest(
        destination="Tokyo",
        start_date="2025-03-01",
        end_date="2025-03-07",
        origin="New York",
        budget=5000,
        travelers=2,
        interests=["food", "culture", "technology"]
    )
    
    print("Starting trip planning stream...")
    async for thought in agent.plan_trip_stream(request):
        print(f"\n[{thought.action.upper()}] {thought.content[:200]}...")
        if thought.data:
            print(f"  Data keys: {list(thought.data.keys())}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["OPENROUTER_API_KEY", "AMADEUS_API_KEY", "AMADEUS_Secret"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"Missing environment variables: {missing}")
        print("Please set them in your .env file")
    else:
        print("All required environment variables found")
        asyncio.run(test_agent())