"""
TravelAI Backend API - Production Ready with Amadeus Integration
No fallbacks, no mock data - Real travel services only
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

# Load environment variables from root directory
load_dotenv(Path(__file__).parent.parent.parent / '.env')

# Import routers
from .routers import flights, hotels, activities, analytics, planner, chat, health

# Import exception handlers
from .core.exceptions import TravelAIException

# Create FastAPI app
app = FastAPI(
    title="TravelAI Backend API",
    description="""
    🚀 **Production Travel API with Amadeus Integration**
    
    Real-time travel data from Amadeus GDS.
    No mock data, no fallbacks - Production ready.
    
    ## Services
    - ✈️ Flights: Search, status, analytics
    - 🏨 Hotels: Search and sentiments
    - 🎯 Activities: Tours and experiences
    - 📊 Analytics: Market insights
    - 🤖 AI: Smart planning and chat
    """,
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(flights.router, prefix="/api/flights", tags=["Flights"])
app.include_router(hotels.router, prefix="/api/hotels", tags=["Hotels"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(planner.router, prefix="/api/planner", tags=["Planner"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])

# Exception handlers
@app.exception_handler(TravelAIException)
async def travel_ai_exception_handler(request: Request, exc: TravelAIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )