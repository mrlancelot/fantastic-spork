"""
This file defines the FastAPI app for the API and all of its routes.
To run this API, use the FastAPI CLI
$ fastapi dev src/api.py
"""

import os
import random
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from convex import ConvexClient

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# The app which manages all of the API routes
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Convex client
convex_url = os.getenv("CONVEX_URL")
if convex_url:
    convex_client = ConvexClient(convex_url)
else:
    convex_client = None


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class StoreUserRequest(BaseModel):
    clerk_user_id: str
    email: str
    name: str | None = None
    image_url: str | None = None


class StoreUserResponse(BaseModel):
    success: bool
    message: str
    user_id: str | None = None


# The decorator declares the function as a FastAPI route on the given path.
# This route in particular is a GET route at "/hello" which returns the example
# dictionary as a JSON response with the status code 200 by default.
@app.get("/hello")
def hello() -> dict[str, str]:
    """Get hello message."""
    return {"message": "Hello from FastAPI"}


# The routes that you specify can also be dynamic, which means that any path
# that follows the format `/items/[some integer]` is valid. When providing
# such path parameters, you'll need to follow this specific syntax and state
# the type of this argument.
#
# This path also includes an optional query parameter called "q". By accessing
# the URL "/items/123456?q=testparam", the JSON response:
#
# { "item_id": 123456, "q": "testparam" }
#
# will be returned. Note that if `item_id` isn't an integer, FastAPI will
# return a response containing an error statement instead of our result.
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None) -> dict[str, int | str | None]:
    return {"item_id": item_id, "q": q}


@app.get("/get-random")
def get_random_item() -> dict[str, int]:
    """Get an item with a random ID."""
    return {"item_id": random.randint(0, 1000)}


@app.get("/test-env")
def test_environment() -> dict[str, str | int]:
    """Test if environment variables are loaded."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "API key not found", "env_file_path": str(env_path)}
    elif api_key == "your_gemini_api_key_here":
        return {"status": "API key found but is placeholder", "env_file_path": str(env_path)}
    else:
        return {"status": "API key loaded", "key_length": len(api_key), "env_file_path": str(env_path)}


@app.post("/chat", response_model=ChatResponse)
async def chat_with_gemini(request: ChatRequest) -> ChatResponse:
    """Chat with Gemini AI using REST API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    if api_key == "your_gemini_api_key_here":
        raise HTTPException(status_code=500, detail="Please replace 'your_gemini_api_key_here' with your actual Gemini API key in the .env file")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": request.message
                    }
                ]
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the text from the response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return ChatResponse(response=parts[0]["text"])
            
            raise HTTPException(status_code=500, detail="Invalid response format from Gemini")
            
        except httpx.ConnectError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Gemini API. Please check your internet connection.")
        except httpx.TimeoutException as e:
            raise HTTPException(status_code=500, detail=f"Request to Gemini API timed out. Please try again.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to Gemini API: {str(e)}")
        except httpx.HTTPStatusError as e:
            error_detail = f"Gemini API error (status {e.response.status_code}): {e.response.text}"
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)


@app.post("/store-user", response_model=StoreUserResponse)
async def store_user_in_convex(request: StoreUserRequest) -> StoreUserResponse:
    """Store a user in Convex database when they authenticate via Clerk."""
    if not convex_client:
        raise HTTPException(
            status_code=500, 
            detail="Convex client not configured. Please set CONVEX_URL in environment variables."
        )
    
    try:
        # Call the Convex mutation to store the user
        mutation_args = {
            "clerkUserId": request.clerk_user_id,
            "email": request.email,
        }
        
        # Only add optional fields if they have values
        if request.name is not None:
            mutation_args["name"] = request.name
        if request.image_url is not None:
            mutation_args["imageUrl"] = request.image_url
            
        result = convex_client.mutation(
            "users:storeFromBackend",
            mutation_args
        )
        
        return StoreUserResponse(
            success=True,
            message="User stored successfully",
            user_id=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store user: {str(e)}"
        )
