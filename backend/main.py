from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import controllers
from controllers.system_controller import router as system_router
from controllers.flights_controller import router as flights_router
from controllers.restaurants_controller import router as restaurants_router
from controllers.hotels_controller import router as hotels_router
from controllers.itinerary_controller import router as itinerary_router
from controllers.video_analysis_controller import router as video_analysis_router

# Create FastAPI app instance
app = FastAPI(
    title="Waypoint Backend API",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(system_router)
app.include_router(flights_router)
app.include_router(restaurants_router)
app.include_router(hotels_router)
app.include_router(itinerary_router)
app.include_router(video_analysis_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
