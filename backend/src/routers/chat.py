"""AI Chat Router - Gemini Integration"""

from fastapi import APIRouter, HTTPException
from ..agents.ai_agent import AIAgent
from ..agents.workflow_agent import WorkflowAgent
from ..models.requests import ChatRequest

router = APIRouter()

# Initialize agents
ai_agent = AIAgent()
workflow_agent = WorkflowAgent()

@router.post("/")
async def chat(request: ChatRequest):
    """
    AI-powered chat using Gemini
    No fallbacks - real AI responses only
    """
    try:
        result = await ai_agent.chat_completion(request.message, request.context)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="AI service unavailable"
            )
        
        return {
            "status": "success",
            "response": result,
            "context": request.context
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI chat error: {str(e)}"
        )

@router.post("/agent")
async def chat_with_agent(request: ChatRequest):
    """Chat with workflow agent for complex queries"""
    try:
        result = await workflow_agent.process_query(request.message, request.context)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Workflow agent unavailable"
            )
        
        return {
            "status": "success",
            "response": result.get("response"),
            "data": result.get("data", {}),
            "action": result.get("action", "general_chat")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow agent error: {str(e)}"
        )