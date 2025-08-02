# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TravelAI - A full-stack AI-powered travel planning platform with React frontend and FastAPI backend, deployed on Vercel.

## Development Workflow

### Quick Start
```bash
# Run both frontend and backend together (recommended)
./run.sh both

# Or run separately:
./run.sh frontend  # React on port 5173
./run.sh backend   # FastAPI on port 8000

# Convex (in separate terminal)
cd frontend && npx convex dev
```

### Development Commands

#### Frontend (React + Vite)
```bash
cd frontend
npm install        # Install dependencies
npm run dev       # Start dev server (port 5173)
npm run build     # Build for production
npm run lint      # Run ESLint
```

#### Backend (FastAPI + Python)
```bash
cd backend
python3 -m venv venv              # Create virtual environment
source venv/bin/activate          # Activate venv (macOS/Linux)
pip install -r requirements.txt   # Install dependencies
fastapi dev src/api.py           # Start dev server (port 8000)
```

## Architecture - Smart Hybrid Approach

### Overview
This project uses a smart hybrid architecture optimized for MVP development while maintaining security and real-time features:

- **Read Operations**: Frontend → Convex (direct)
  - Real-time updates via Convex subscriptions
  - Optimal performance for data fetching
  - Automatic caching and synchronization

- **Write Operations**: Frontend → Backend → Convex
  - Server-side validation and business logic
  - Secure handling of sensitive operations
  - Audit trail capabilities

- **External APIs**: Frontend → Backend → (Gemini, Stripe, etc.)
  - API keys stay secure on backend
  - Rate limiting and error handling
  - Response caching when appropriate

### Benefits of This Approach
1. **Real-time where it matters**: Users see instant updates when data changes
2. **Security for writes**: All mutations go through backend validation
3. **Minimal complexity**: Leverages Convex's strengths while maintaining control
4. **Easy to evolve**: Can gradually move more operations to backend as needed

### Project Structure
```
fantastic-spork/
├── frontend/                    # React application
│   ├── src/                    # Source code
│   │   ├── components/         # Reusable components
│   │   ├── App.jsx            # Main app with routing
│   │   └── main.jsx           # Entry point with providers
│   ├── convex/                # Convex functions
│   │   ├── schema.ts          # Database schema
│   │   ├── users.ts           # User queries/mutations
│   │   └── trips.ts           # Trip queries/mutations
│   └── package.json
├── backend/                   # FastAPI application
│   ├── src/
│   │   ├── api.py            # API routes
│   │   └── main.py           # Production server
│   └── requirements.txt
├── api/                      # Vercel serverless function
│   └── index.py             # Entry point for Vercel
├── vercel.json              # Vercel configuration
└── run.sh                   # Development helper
```

### Vercel Configuration
The `vercel.json` file configures:
- Frontend build process
- Backend as serverless function
- Routing rules for API and SPA

## Development Guidelines

### Pattern 1: Reading Data (Direct from Convex)
Use Convex queries for all read operations to get real-time updates:

```jsx
// frontend/src/components/TripList.jsx
import { useQuery } from 'convex/react';
import { api } from '../convex/_generated/api';

export function TripList() {
  // Direct query to Convex - real-time updates!
  const trips = useQuery(api.trips.getUserTrips);
  
  if (!trips) return <div>Loading...</div>;
  
  return (
    <div>
      {trips.map(trip => (
        <TripCard key={trip._id} trip={trip} />
      ))}
    </div>
  );
}
```

### Pattern 2: Writing Data (Through Backend API)
Use backend API for all write operations to ensure validation:

```jsx
// frontend/src/components/CreateTrip.jsx
import { useState } from 'react';

export function CreateTrip() {
  const [loading, setLoading] = useState(false);
  
  const handleCreateTrip = async (tripData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/trips`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tripData)
      });
      
      if (!response.ok) throw new Error('Failed to create trip');
      
      const result = await response.json();
      // Success! Convex will automatically update any queries
    } catch (error) {
      console.error('Error creating trip:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleCreateTrip}>
      {/* Form fields */}
    </form>
  );
}
```

### Pattern 3: External API Calls (Through Backend)
Always route external API calls through the backend:

```jsx
// frontend/src/components/ChatInterface.jsx
export function ChatInterface() {
  const sendMessage = async (message) => {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    
    const data = await response.json();
    return data.response;
  };
}
```

### Backend API Implementation
When creating backend endpoints that interact with Convex:

```python
# backend/src/api.py
from convex import ConvexClient

convex_client = ConvexClient(os.getenv("CONVEX_URL"))

@app.post("/api/trips")
async def create_trip(request: TripRequest):
    # 1. Validate request data
    if not request.destination:
        raise HTTPException(status_code=400, detail="Destination required")
    
    # 2. Apply business logic
    if request.budget and request.budget < 0:
        raise HTTPException(status_code=400, detail="Budget must be positive")
    
    # 3. Store in Convex via backend
    try:
        result = convex_client.mutation(
            "trips:createFromBackend",
            {
                "destination": request.destination,
                "startDate": request.start_date,
                "endDate": request.end_date,
                "budget": request.budget
            }
        )
        return {"status": "success", "trip_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## API Communication Patterns

### API Helper Utility
Create a centralized API helper for consistency:

```javascript
// frontend/src/utils/api.js
const API_BASE = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : '';

export async function apiCall(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}/api/${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  
  return response.json();
}

// Specific API functions
export const api = {
  trips: {
    create: (data) => apiCall('trips', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiCall(`trips/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiCall(`trips/${id}`, { method: 'DELETE' })
  },
  chat: {
    send: (message) => apiCall('chat', { method: 'POST', body: JSON.stringify({ message }) })
  },
  user: {
    store: (data) => apiCall('store-user', { method: 'POST', body: JSON.stringify(data) })
  }
};
```

## Data Flow Examples

### Example 1: User Views Dashboard
```
1. Component mounts
2. useQuery(api.trips.getUserTrips) executes
3. Convex returns trips in real-time
4. If another user/tab creates a trip, dashboard updates automatically
```

### Example 2: User Creates Trip
```
1. User fills form and submits
2. Frontend calls api.trips.create(data)
3. Backend validates data
4. Backend stores in Convex via mutation
5. All frontend queries automatically update
```

### Example 3: User Chats with AI
```
1. User types message
2. Frontend calls api.chat.send(message)
3. Backend calls Gemini API
4. Backend stores conversation in Convex
5. Frontend shows response
```

## Architecture Decision Record

### Why This Hybrid Approach?

**Context**: Building an MVP for a travel planning platform with real-time features.

**Decision**: Use Convex directly for reads, backend API for writes.

**Rationale**:
1. **Development Speed**: Convex queries are simple and real-time out of the box
2. **Security**: Backend validates all mutations
3. **Flexibility**: Can easily move operations to backend later
4. **Performance**: No unnecessary API calls for reading data

**Consequences**:
- ✅ Faster MVP development
- ✅ Real-time features work immediately
- ✅ Secure write operations
- ⚠️ Two patterns to learn (but both are simple)
- ⚠️ Frontend has Convex dependency (acceptable for MVP)

**Future Migration Path**:
If needed, we can gradually move read operations to backend by:
1. Creating GET endpoints in backend
2. Replacing useQuery with API calls
3. Implementing WebSockets for real-time updates

## Key API Endpoints

### Backend API (FastAPI)
- `POST /api/chat` - AI chat with Gemini
- `POST /api/store-user` - Store user in Convex (called by AuthWrapper)
- `POST /api/trips` - Create a new trip (TODO)
- `PUT /api/trips/{id}` - Update a trip (TODO)
- `DELETE /api/trips/{id}` - Delete a trip (TODO)
- `GET /api/hello` - Health check
- `GET /api/test-env` - Environment check

### Convex Functions (Frontend Access)
**Queries (Direct Access)**
- `users.getMyUser` - Get current user
- `trips.getUserTrips` - Get user's trips
- `trips.getTrip` - Get specific trip

**Mutations (Through Backend Only)**
- `users.storeFromBackend` - Store user data
- `trips.createFromBackend` - Create trip (TODO)
- `trips.updateFromBackend` - Update trip (TODO)
- `trips.deleteFromBackend` - Delete trip (TODO)

## Environment Variables

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key
CLERK_SECRET_KEY=sk_test_...
CONVEX_URL=https://...convex.cloud
CONVEX_DEPLOYMENT=production
```

### Frontend (.env.local)
```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_CONVEX_URL=https://...convex.cloud
```

### Vercel (set in dashboard)
All backend environment variables need to be set in Vercel project settings.

## Common Development Tasks

### Adding a New Feature

1. **Determine if it's a read or write operation**
   - Reading data? Use Convex query directly
   - Writing data? Create backend endpoint first
   - External API? Always go through backend

2. **For Read Operations**
   ```jsx
   const data = useQuery(api.features.getData);
   ```

3. **For Write Operations**
   - Create backend endpoint
   - Add validation and business logic
   - Call Convex mutation from backend
   - Use API helper in frontend

### Adding AI Features
1. Design the prompt in backend
2. Create endpoint in `backend/src/api.py` using Gemini
3. Add frontend UI to call the endpoint
4. Store results in Convex if needed

### Testing API Endpoints
```bash
# Test locally
curl http://localhost:8000/api/hello

# Test with FastAPI docs
open http://localhost:8000/docs
```

## Deployment Process

### Deploy to Vercel
```bash
# From root directory
vercel

# Or push to GitHub (if connected)
git push origin main
```

### What Happens During Deployment
1. Vercel runs build commands from `vercel.json`
2. Frontend is built with Vite
3. Backend is packaged as serverless function
4. Routes are configured for API and SPA

## Important Patterns

### Error Handling
```python
# Backend
@app.post("/api/endpoint")
async def endpoint(request: Request):
    try:
        # Validation
        # Business logic
        # Convex operation
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")
```

```javascript
// Frontend
try {
  const data = await apiCall('endpoint', { method: 'POST' });
  // Handle success
} catch (error) {
  // Show user-friendly error
  console.error('Error:', error);
}
```

### Authentication Flow
1. User signs in with Clerk
2. Frontend gets user data
3. Frontend calls `/api/store-user`
4. Backend stores in Convex
5. User can access features

## Debugging Tips

### Frontend Issues
- Check browser console
- Verify API URLs (dev vs prod)
- Check network tab for API calls
- Ensure Convex queries have proper auth

### Backend Issues
- Check terminal running FastAPI
- Use `/docs` for API testing
- Add print statements for debugging
- Verify Convex client initialization

### Vercel Issues
- Check function logs in Vercel dashboard
- Verify environment variables
- Test build locally with `vercel dev`

## Do's and Don'ts

### Do's
- ✅ Use Convex queries for all read operations
- ✅ Use backend API for all write operations
- ✅ Keep validation logic in backend
- ✅ Handle errors gracefully in both patterns
- ✅ Test locally before deploying
- ✅ Use TypeScript for Convex functions
- ✅ Document why a feature uses backend vs direct Convex

### Don'ts
- ❌ Don't call Convex mutations directly from frontend
- ❌ Don't put business logic in Convex functions
- ❌ Don't expose API keys in frontend
- ❌ Don't mix patterns in the same component
- ❌ Don't skip validation on backend endpoints
- ❌ Don't create complex Convex actions (use backend instead)
- ❌ Don't fight the pattern - embrace the hybrid approach