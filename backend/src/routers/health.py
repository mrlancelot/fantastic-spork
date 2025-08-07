"""Health and System Status Router"""

import os
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "travelai-backend",
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "amadeus": bool(os.getenv("AMADEUS_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "openrouter": bool(os.getenv("OPENROUTER_API_KEY"))
        }
    }

@router.get("/status")
async def status():
    """Detailed status check"""
    amadeus_configured = bool(os.getenv("AMADEUS_API_KEY") and os.getenv("AMADEUS_Secret"))
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    
    if not amadeus_configured:
        raise HTTPException(
            status_code=503,
            detail="Amadeus API not configured. Set AMADEUS_API_KEY and AMADEUS_Secret in .env"
        )
    
    return {
        "status": "operational",
        "amadeus": "configured" if amadeus_configured else "missing",
        "ai": "configured" if gemini_configured else "missing",
        "timestamp": datetime.now().isoformat()
    }