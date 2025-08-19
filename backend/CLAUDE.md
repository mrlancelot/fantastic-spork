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

**Install Playwright browsers (required for flight_search.py):**
```bash
playwright install chromium
```

**Testing:**
No formal test framework is configured. The application provides interactive API documentation at http://localhost:8000/docs for manual testing.

## Architecture Overview

This is a Python FastAPI backend with AI agent capabilities for travel planning:

**Core Components:**
- `main.py` - FastAPI application with REST endpoints and CORS configuration
- `agent.py` - Basic AI agent functionality using LlamaIndex with Gemini LLM and MCP tools
- `agents/` - Specialized travel agents:
  - `flight_agent.py` - Flight search using BrightData MCP
  - `flight_search.py` - Alternative flight search using Playwright and Gemini API
  - `restaurant_agent.py` - Restaurant search using Tavily MCP
  - `hotel_agent.py` - Hotel search using BrightData MCP
  - `itinerary_writer.py` - Itinerary writing orchestration service
- `service/exceptions.py` - Custom exception hierarchy for error handling

**Key Patterns:**
- Uses Pydantic models for request/response validation
- In-memory storage with simple counters for IDs (not production-ready)
- Async/await pattern throughout for better performance
- Integration with external AI services (Google Gemini, BrightData MCP, Tavily MCP)
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
- `GOOGLE_API_KEY` - For Gemini LLM
- `BRIGHT_DATA_API_TOKEN` - For BrightData MCP (flights, hotels)
- `TAVILY_API_KEY` - For Tavily MCP (restaurants)
- `GEMINI_API_KEY` - For direct Gemini API calls in flight_search.py

**AI Agent Architecture:**
- LlamaIndex FunctionAgent and ReActAgent implementations
- MCP (Model Context Protocol) integration for web scraping
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
- The flight_search.py module uses Playwright for browser automation (requires browser installation)