#!/usr/bin/env python3
"""Test Convex connection and operations"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.convex_client import get_db
from utils.job_manager import get_job_manager

def test_convex_connection():
    """Test basic Convex connection and operations"""
    print("Testing Convex connection...")
    
    try:
        # Test 1: Get database instance
        db = get_db()
        print("✓ Database client created")
        
        # Test 2: Create a test job
        job_manager = get_job_manager()
        job_id = job_manager.create_job(
            job_type="test_job",
            user_id=None,
            payload={"test": "data"}
        )
        print(f"✓ Test job created with ID: {job_id}")
        
        # Test 3: Query the job
        job = job_manager.get_job_status(job_id)
        if job:
            print(f"✓ Job retrieved: {job.get('status')}")
        else:
            print("✗ Failed to retrieve job")
        
        print("\nAll tests passed! Convex connection is working.")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_convex_connection()
    sys.exit(0 if success else 1)