# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Virtual Environment Setup:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run the Application:**
```bash
python main.py
# Or directly with uvicorn:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```


**Testing:**
No formal test framework is configured. The application provides interactive API documentation at http://localhost:8000/docs for manual testing.

## Architecture Overview

This is a Python FastAPI backend with AI agent capabilities for travel planning:

**Core Components:**
- `main.py` - FastAPI application with REST endpoints and CORS configuration
- `agent.py` - Basic AI agent functionality using LlamaIndex with Gemini LLM and MCP tools
- `agents/` - Specialized travel agents:
  - `flight_agent.py` - Flight search agent
  - `flight_search.py` - Alternative flight search implementation
  - `restaurant_agent.py` - Restaurant search using Tavily MCP
  - `hotel_agent.py` - Hotel search agent
  - `itinerary_writer.py` - Itinerary writing orchestration service
- `service/` - Service layer:
  - `api_utils.py` - OpenRouter API integration for URL generation and web scraping
  - `flight_service.py` - Flight search service using Kayak
  - `hotel_service.py` - Hotel search service using Booking.com and Airbnb
  - `exceptions.py` - Custom exception hierarchy for error handling

**Key Patterns:**
- Uses Pydantic models for request/response validation
- In-memory storage with simple counters for IDs (not production-ready)
- Async/await pattern throughout for better performance
- Integration with OpenRouter API for AI-powered URL generation and data extraction
- Lightweight httpx-based web scraping (no Playwright dependency)
- Agent workflow orchestration with streaming capabilities

**API Structure:**
- Standard CRUD endpoints for items and users
- AI agent endpoints:
  - `/discovery/recommendations` - Calculator demo
  - `/agent/basic` - Basic LLM completion
  - `/test` - MCP web scraping test
  - `/agent/workflow` - Orchestrated multi-agent workflow
  - `/flights` - Flight search endpoint
  - `/restaurants` - Restaurant search endpoint
- Health check at `/health`

**Environment Dependencies:**
Required environment variables in `.env`:
- `OPENROUTER_API_KEY` - For AI-powered URL generation and data extraction (Required)
- `GOOGLE_API_KEY` - For Gemini LLM
- `TAVILY_API_KEY` - For Tavily MCP (restaurants)
- `GEMINI_API_KEY` - For direct Gemini API calls

**AI Agent Architecture:**
- LlamaIndex FunctionAgent and ReActAgent implementations
- OpenRouter API integration with multiple models:
  - Google Gemini 2.5 Flash Lite for hotel searches
  - Z.AI GLM-4 32B for flight searches and data processing
- Lightweight web scraping using httpx and BeautifulSoup
- Structured output using Pydantic models
- Configurable system prompts for different agent behaviors
- Agent workflow orchestration with event streaming

## Key Considerations

- All API origins are allowed (`allow_origins=["*"]`) - should be restricted in production
- No authentication or authorization implemented
- Database operations use in-memory lists - replace with proper database for production
- Error handling uses custom exception hierarchy in `service/exceptions.py`
- No logging configuration beyond FastAPI defaults and basic logger setup
- Agents use various external services that require API tokens
- Flight and hotel services use OpenRouter API for URL generation and lightweight scraping
- No browser automation dependencies - fully compatible with serverless deployments