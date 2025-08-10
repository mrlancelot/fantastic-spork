"""
Vercel serverless function entry point for TravelAI Backend
"""

import sys
import os

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

# Import the main FastAPI app
from api_server import app

# Export the FastAPI app for Vercel
# Vercel will handle the /api routing through rewrites in vercel.json
