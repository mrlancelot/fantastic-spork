"""Test script to debug import issues"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

print(f"Current working directory: {os.getcwd()}")
print(f"Added to sys.path: {src_dir}")
print(f"Full sys.path: {sys.path[:5]}...")  # Show first 5 entries

# Try imports
print("\n=== Testing Imports ===")

try:
    from services.flights import AmadeusFlightService, FlightSearchRequest
    print("✓ Flight service import successful")
except ImportError as e:
    print(f"✗ Flight service import failed: {e}")

try:
    from services.hotel_agent import HotelAgent
    print("✓ Hotel agent import successful")
except ImportError as e:
    print(f"✗ Hotel agent import failed: {e}")

try:
    from services.restaurant_agent import RestaurantAgent
    print("✓ Restaurant agent import successful")
except ImportError as e:
    print(f"✗ Restaurant agent import failed: {e}")

# Try importing the master agent
print("\n=== Testing Master Agent Import ===")
try:
    from agents.master_agent import MasterTravelAgent
    print("✓ Master agent import successful")
    
    # Try creating an instance
    agent = MasterTravelAgent()
    print("✓ Master agent instantiated successfully")
except ImportError as e:
    print(f"✗ Master agent import failed: {e}")
except Exception as e:
    print(f"✗ Master agent instantiation failed: {e}")

print("\n=== Available modules in services directory ===")
services_dir = src_dir / 'services'
if services_dir.exists():
    for file in services_dir.glob('*.py'):
        print(f"  - {file.name}")
else:
    print("Services directory not found!")

print("\n=== Available modules in agents directory ===")
agents_dir = src_dir / 'agents'
if agents_dir.exists():
    for file in agents_dir.glob('*.py'):
        print(f"  - {file.name}")
else:
    print("Agents directory not found!")