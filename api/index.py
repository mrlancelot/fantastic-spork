"""
This is only if you are deploying on Vercel.
If you are not deploying on Vercel, you can delete this file.
"""

import sys
import os

# Add backend to path for the new refactored structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the main FastAPI app from the refactored backend
from main import app

# Export the FastAPI app for Vercel
# Note: We don't need to mount it at /api since Vercel's rewrites handle that
