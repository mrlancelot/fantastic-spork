"""Smart Planner Router - AI-Powered Itinerary Creation"""

from fastapi import APIRouter, HTTPException, Request
from ..services.smart_planner import SmartPlannerService
from ..models.requests import SmartPlannerRequest
import uuid

router = APIRouter()

# Initialize service
planner_service = SmartPlannerService()

@router.post("/smart")
async def create_smart_itinerary(request: SmartPlannerRequest):
    """
    Create AI-powered smart itinerary
    Uses real Amadeus data for flights, hotels, and activities
    """
    try:
        result = await planner_service.create_smart_itinerary(request)
        
        if not result.get("itinerary"):
            raise HTTPException(
                status_code=500,
                detail="Failed to create itinerary"
            )
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Smart planner error: {str(e)}"
        )

@router.post("/save")
async def save_itinerary(request: Request):
    """Save itinerary to database"""
    try:
        body = await request.json()
        result = await planner_service.save_itinerary(body)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Save itinerary error: {str(e)}"
        )

@router.put("/slot/{date}/{slot_id}")
async def update_slot(date: str, slot_id: str, request: Request):
    """Update a specific slot in the itinerary"""
    try:
        body = await request.json()
        result = await planner_service.update_slot(date, slot_id, body)
        
        return {
            "status": "success",
            "message": f"Slot {slot_id} updated for {date}",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Slot update error: {str(e)}"
        )

@router.post("/slot/complete")
async def complete_slot(request: Request):
    """Mark a slot as completed"""
    try:
        body = await request.json()
        slot_id = body.get("slot_id")
        
        if not slot_id:
            raise HTTPException(
                status_code=400,
                detail="slot_id is required"
            )
        
        result = await planner_service.complete_slot(slot_id)
        
        return {
            "status": "success",
            "message": "Slot completed!",
            "celebration": True,
            "slot_id": slot_id,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Slot completion error: {str(e)}"
        )