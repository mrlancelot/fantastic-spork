#!/usr/bin/env python3
"""Test script for the day planner agent to verify unique activity generation"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from agents.day_planner_agent import DayPlannerAgent

async def test_day_planner():
    """Test that day planner generates unique activities for each day"""
    
    planner = DayPlannerAgent()
    previous_activities = []
    
    print("Testing Day Planner Agent - Generating 6 days of activities for Tokyo")
    print("=" * 70)
    
    for day in range(1, 7):
        print(f"\nDay {day}:")
        
        # Get activities for this day
        activities = await planner.plan_day(
            destination="Tokyo",
            day_num=day,
            total_days=6,
            previous_activities=previous_activities,
            interests=["food", "culture", "adventure"]
        )
        
        # Print activities
        for time_slot, activity in activities.items():
            print(f"  {time_slot.capitalize():10} - {activity}")
        
        # Track activities to ensure no repetition
        day_activities = list(activities.values())
        
        # Check for duplicates
        duplicates = [a for a in day_activities if a in previous_activities]
        if duplicates:
            print(f"  ⚠️  WARNING: Duplicate activities found: {duplicates}")
        else:
            print(f"  ✅ All activities are unique!")
        
        previous_activities.extend(day_activities)
    
    print("\n" + "=" * 70)
    print(f"Total unique activities generated: {len(set(previous_activities))}/{len(previous_activities)}")
    
    # Check overall uniqueness
    if len(set(previous_activities)) == len(previous_activities):
        print("✅ SUCCESS: All activities across all days are unique!")
    else:
        print("⚠️  Some activities were repeated")

if __name__ == "__main__":
    asyncio.run(test_day_planner())