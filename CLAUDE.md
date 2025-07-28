# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TravelAI - A full-stack AI-powered travel planning platform with React frontend and FastAPI backend.

## Development Commands

### Frontend (React + Vite)
```bash
cd frontend
npm install        # Install dependencies
npm run dev       # Start dev server (port 5173)
npm run build     # Build for production
npm run lint      # Run ESLint
```

### Backend (FastAPI + Python)
```bash
cd backend
python3 -m venv venv              # Create virtual environment
source venv/bin/activate          # Activate venv (macOS/Linux)
pip install -r requirements.txt   # Install dependencies
fastapi dev src/api.py           # Start dev server (port 8000)
```

### Full Stack Development
```bash
./run.sh both      # Run frontend and backend together
./run.sh frontend  # Run only frontend
./run.sh backend   # Run only backend
```

## Architecture

### Project Structure
- **Monorepo** with separate `frontend/` and `backend/` directories
- **Frontend**: React 18 SPA with Vite, Tailwind CSS, and Lucide icons
- **Backend**: FastAPI with Gemini AI integration, served on port 8000
- **Deployment**: Supports Docker, Vercel, and Render

### Key API Endpoints
- `POST /chat` - Gemini AI chat integration for travel assistance
- `GET /hello` - Health check endpoint
- `GET /items/{item_id}` - Example parametric route
- `GET /get-random` - Random item generator
- `GET /test-env` - Environment variable verification

### Important Patterns
- **API Communication**: Frontend makes requests to backend at `http://localhost:8000`
- **Static Files**: In production, FastAPI serves the built frontend from `dist/`
- **Environment Variables**: Backend requires `GEMINI_API_KEY` in `.env` file
- **CORS**: Configured for localhost:5173 in development

## Deployment

### Docker
```bash
docker build . -t my-app
docker run --rm -it -p 8000:8000 my-app
```

### Vercel
```bash
vercel  # Deploy from root directory
```
Configuration in `vercel.json` sets up serverless functions for the backend.

### Environment Setup
Backend requires a `.env` file with:
```
GEMINI_API_KEY=your_api_key_here
```

## Key Files to Know
- `backend/src/api.py` - Main FastAPI application and routes
- `frontend/src/App.jsx` - Main React component with routing
- `frontend/src/components/` - Reusable UI components
- `vercel.json` - Vercel deployment configuration
- `Dockerfile` - Multi-stage build for production