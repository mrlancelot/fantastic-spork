# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Frontend Development
```bash
cd frontend
npm install                # Install dependencies
npm run dev                # Start development server on http://localhost:5173
npm run build             # Build for production (TypeScript check + Vite build)
npm run lint              # Run ESLint
npm run preview           # Preview production build
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the backend server
python main.py            # Runs on http://localhost:8000
# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running All Services
```bash
./run.sh all              # Starts frontend, backend, and Convex
./run.sh frontend         # Only frontend
./run.sh backend          # Only backend
./run.sh convex          # Only Convex
```

### Convex Database
```bash
cd frontend
npx convex dev           # Start Convex development server
```

### Linting
```bash
# Backend Python linting
cd backend && ruff check .

# Frontend TypeScript/React linting  
cd frontend && npm run lint
```

## Architecture

This is a full-stack travel planning application with a three-tier architecture:

### Frontend (React + TypeScript + Vite)
- **Location**: `/frontend`
- **Framework**: React 18 with TypeScript, built with Vite
- **Styling**: Tailwind CSS with custom primary color scheme
- **Routing**: React Router v6 for SPA navigation
- **State Management**: React hooks with context where needed
- **Key Libraries**: 
  - `lucide-react` for icons
  - `date-fns` for date formatting
  - `@dnd-kit` for drag-and-drop functionality

### Backend (FastAPI + Python)
- **Location**: `/backend`
- **Framework**: FastAPI with async/await patterns
- **Architecture**: Controller-based routing with service layer
- **Controllers**:
  - `system_controller` - Health checks and system status
  - `flights_controller` - Flight search via Amadeus API
  - `hotels_controller` - Hotel search and recommendations
  - `restaurants_controller` - Restaurant discovery
  - `itinerary_controller` - AI-powered itinerary generation
  - `video_analysis_controller` - Travel video analysis
- **AI Integration**: 
  - Google Gemini for itinerary generation
  - OpenRouter for multi-model AI support
  - LlamaIndex for agent orchestration
- **External APIs**:
  - Amadeus GDS for real flight/hotel data
  - Tavily for restaurant search
  - BrightData for web scraping

### Database Layer (Convex)
- **Type**: Real-time serverless database
- **Features**: 
  - Real-time subscriptions for instant updates
  - Direct frontend queries for reads (performance)
  - Backend mutations for writes (security)
- **Location**: Frontend Convex functions are removed from the current codebase (per git status)

## Key Design Patterns

1. **Hybrid Data Access**: 
   - Frontend reads directly from Convex for real-time updates
   - All writes go through backend for validation and business logic

2. **Service-Controller Pattern** (Backend):
   - Controllers handle HTTP requests/responses
   - Services encapsulate business logic and external API calls
   - Clean separation of concerns

3. **Component-Based Architecture** (Frontend):
   - Reusable UI components in `/frontend/src/components`
   - Page components in `/frontend/src/pages`
   - Shared design system components in `/frontend/src/design-system`

4. **Type Safety**:
   - Full TypeScript on frontend
   - Pydantic models for backend request/response validation

## Environment Configuration

Required environment variables (create `.env` in root):

```env
# Authentication
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Database  
CONVEX_URL=https://...convex.cloud
CONVEX_DEPLOYMENT=dev:...

# Travel APIs
AMADEUS_API_KEY=...
AMADEUS_Secret=...

# AI Services
GEMINI_API_KEY=...
OPENROUTER_API_KEY=sk-or-v1-...

# Frontend
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_CONVEX_URL=https://...convex.cloud
VITE_API_URL=http://localhost:8000
```

## Development Workflow

1. **Frontend Changes**: Edit TypeScript/React files in `/frontend/src`, Vite hot-reloads automatically
2. **Backend Changes**: Edit Python files in `/backend`, uvicorn auto-reloads with `--reload` flag
3. **API Testing**: Use Swagger UI at http://localhost:8000/docs
4. **Type Checking**: Frontend builds run `tsc` automatically

## Current State Notes

Based on git status, the project is undergoing refactoring:
- Convex functions have been removed from frontend
- Backend has new modular structure with controllers and services
- Frontend has been converted to TypeScript with new component structure

## Testing

Currently no formal test framework is configured. Testing approaches:
- **Backend**: Use Swagger UI at `/docs` for API testing
- **Frontend**: Manual testing in development mode
- **End-to-end**: No Playwright tests configured yet despite dependency

## Important Considerations

- CORS is currently set to allow all origins (`*`) - restrict in production
- No authentication middleware implemented yet (Clerk keys present but not integrated)
- Using test Amadeus environment with limited data availability
- In-memory storage patterns in some backend services (not production-ready)