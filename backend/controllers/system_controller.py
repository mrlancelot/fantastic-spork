from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/")
async def root():
    return {"message": "Welcome to Waypoint Backend API", "version": "1.0.0"}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "waypoint-backend"}
