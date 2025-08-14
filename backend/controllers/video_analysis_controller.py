from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from service.video_analysis import analyze_video_for_activities

router = APIRouter(tags=["Video Analysis"])


class VideoAnalysisRequest(BaseModel):
    video_url: str


@router.post("/analyze-video")
async def analyze_video(request: VideoAnalysisRequest) -> dict:
    try:
        result = await analyze_video_for_activities(request.video_url)
        return {
            "video_info": result.get("video_info", {}),
            "activities": result.get("activities", []),
            "analysis_confidence": result.get("analysis_metadata", {}).get("analysis_confidence", "medium")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")
