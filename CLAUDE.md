# CLAUDE.md

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TravelAI - A full-stack AI-powered travel planning platform built with modern web technologies:
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.8+
- **Database**: Convex (real-time, serverless)
- **Authentication**: Clerk (Google OAuth + Email/Password)
- **AI Integration**: Google Gemini API

## Development Commands

### Frontend (React + Vite)
```bash
cd frontend
npm install        # Install dependencies
npm run dev       # Start dev server (port 5173)
npm run build     # Build for production
npm run lint      # Run ESLint
npm run preview   # Preview production build
```

### Backend (FastAPI + Python)
```bash
cd backend
python3 -m venv venv              # Create virtual environment
source venv/bin/activate          # Activate venv (macOS/Linux)
# On Windows: venv\Scripts\activate
pip install -r requirements.txt   # Install dependencies
fastapi dev src/api.py           # Start dev server (port 8000)
fastapi run src/main.py          # Production server
```

### Convex Database
```bash
cd frontend
npx convex dev    # Run development server
npx convex deploy # Deploy to production
```

### Full Stack Development
```bash
./run.sh both      # Run frontend and backend together
./run.sh frontend  # Run only frontend
./run.sh backend   # Run only backend
```

## Architecture

### Project Structure
```
fantastic-spork/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   │   ├── AuthWrapper.jsx # Authentication wrapper
│   │   │   ├── SignInPage.jsx  # Clerk sign-in integration
│   │   │   ├── SignUpPage.jsx  # Clerk sign-up integration
│   │   │   ├── TripForm.jsx    # Trip creation form
│   │   │   ├── ConvexDebug.jsx # Convex debugging component
│   │   │   └── [other components]
│   │   ├── pages/              # Page components
│   │   │   ├── Home.jsx        # Landing page
│   │   │   ├── Dashboard.jsx   # User dashboard
│   │   │   ├── Itinerary.jsx   # Trip itinerary view
│   │   │   └── [other pages]
│   │   ├── App.jsx             # Main app component with routing
│   │   ├── main.jsx            # Application entry point
│   │   └── index.css           # Global styles
│   ├── convex/                 # Convex backend functions
│   │   ├── _generated/         # Auto-generated Convex files
│   │   ├── schema.ts           # Database schema definitions
│   │   ├── users.ts            # User management functions
│   │   ├── trips.ts            # Trip CRUD operations
│   │   ├── chats.ts            # AI chat history
│   │   └── auth.config.js      # Clerk auth configuration
│   ├── public/                 # Static assets
│   ├── package.json
│   ├── vite.config.js
│   └── .env.local              # Frontend environment variables
├── backend/                    # FastAPI backend application
│   ├── src/
│   │   ├── api.py             # FastAPI routes and endpoints
│   │   ├── main.py            # Server configuration
│   │   └── models/            # Pydantic models (if any)
│   ├── requirements.txt        # Python dependencies
│   └── .env                   # Backend environment variables
├── api/                       # Vercel serverless functions
│   └── index.py              # Vercel function entry point
├── tests/                     # Playwright E2E tests
│   ├── playwright.config.ts
│   └── e2e/
├── .mcp.json                  # MCP server configuration
├── claude_desktop_config.json # Claude Desktop MCP config
├── run.sh                     # Development utility script
├── Dockerfile                 # Docker build configuration
├── vercel.json               # Vercel deployment settings
├── DEPLOYMENT.md             # Deployment documentation
├── CLAUDE.md                 # This file
└── README.md                 # Project documentation
```

### Technology Stack Details

#### Frontend Technologies
- **React 18**: Component-based UI with hooks
- **Vite**: Lightning-fast build tool with HMR
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Modern icon library
- **React Router**: Client-side routing
- **Clerk React**: Authentication components
- **Convex React**: Real-time data hooks

#### Backend Technologies
- **FastAPI**: Modern async Python web framework
- **Pydantic**: Data validation with type hints
- **CORS Middleware**: Cross-origin request handling
- **Google Generative AI**: Gemini API integration
- **Convex Python SDK**: Database operations
- **python-dotenv**: Environment variable management

#### Database (Convex)
- **Real-time sync**: Automatic data synchronization
- **Serverless functions**: Backend logic in TypeScript
- **Type-safe queries**: End-to-end type safety
- **Built-in auth**: Integration with Clerk

### Key API Endpoints

#### Backend API (FastAPI)
```python
# Health check
GET /hello
Response: {"message": "Hello from FastAPI"}

# AI Chat endpoint
POST /chat
Body: {"message": "Plan a trip to Paris"}
Response: {"response": "AI-generated travel advice..."}

# Store user in Convex
POST /store-user
Body: {"userId": "clerk_id", "email": "user@example.com"}
Response: {"status": "success", "convexId": "..."}

# Environment test
GET /test-env
Response: {"gemini_configured": true}

# Static file serving (production)
GET /{path}
Serves React build files from public/
```

#### Convex Functions
```typescript
// User management
users.store({ userId, email, name })
users.storeFromBackend({ userId, email })
users.getMyUser()
users.getUserById({ userId })

// Trip management
trips.create({ title, destination, startDate, endDate })
trips.getUserTrips()
trips.getTripById({ tripId })
trips.updateTrip({ tripId, updates })
trips.deleteTrip({ tripId })

// Chat/AI functions
chats.sendMessage({ message, tripId })
chats.getChatHistory({ tripId })
```

### Important Patterns

#### API Communication
- Frontend makes requests to backend at `http://localhost:8000`
- In production, relative URLs are used (`/api/...`)
- All API calls should handle errors gracefully
- Use proper loading states for async operations

#### Authentication Flow
1. User signs in with Clerk (frontend)
2. Clerk provides user token and metadata
3. Frontend calls backend `/store-user` endpoint
4. Backend stores user in Convex database
5. User session is maintained by Clerk

#### State Management
- Local component state for UI interactions
- Convex for persistent data (trips, users, chats)
- React Context for global UI state (if needed)
- URL parameters for shareable state

#### Error Handling
- Frontend: Try-catch blocks with user-friendly messages
- Backend: FastAPI exception handlers
- Convex: Built-in error handling with retry logic
- Display errors in UI, don't just console.log

#### Environment Variables
Frontend (.env.local):
```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_CONVEX_URL=https://...convex.cloud
```

Backend (.env):
```
GEMINI_API_KEY=your_gemini_api_key
CLERK_SECRET_KEY=sk_test_...
CONVEX_URL=https://...convex.cloud
CONVEX_DEPLOYMENT=production
```

## Development Guidelines

### Code Style
- **Frontend**: ESLint configuration in place
- **Backend**: Follow PEP 8 for Python code
- **TypeScript**: Strict mode enabled for Convex
- **Formatting**: Use Prettier for consistent formatting

### Component Structure
```jsx
// Example React component structure
import { useState, useEffect } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../convex/_generated/api';

export function ComponentName() {
  // Hooks first
  const [state, setState] = useState();
  const data = useQuery(api.trips.getUserTrips);
  const createTrip = useMutation(api.trips.create);
  
  // Effects
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  // Handlers
  const handleSubmit = async () => {
    await createTrip({ /* data */ });
  };
  
  // Render
  return (
    <div className="tailwind-classes">
      {/* JSX */}
    </div>
  );
}
```

### API Route Structure
```python
# Example FastAPI route structure
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RequestModel(BaseModel):
    field: str

@router.post("/endpoint")
async def endpoint_name(request: RequestModel):
    try:
        # Business logic
        result = process_request(request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Database Schema (Convex)
```typescript
// Example Convex schema
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    userId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    createdAt: v.number(),
  }).index("by_userId", ["userId"]),
  
  trips: defineTable({
    userId: v.string(),
    title: v.string(),
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    budget: v.optional(v.number()),
    activities: v.array(v.object({
      day: v.number(),
      items: v.array(v.string()),
    })),
  }).index("by_user", ["userId"]),
});
```

## Deployment

### Docker
```bash
# Build and run with Docker
docker build -t travelai .
docker run -p 8000:8000 --env-file .env travelai
```

The Dockerfile uses a multi-stage build:
1. Stage 1: Build React frontend with Node
2. Stage 2: Set up Python backend and copy built frontend

### Vercel
```bash
# Deploy to Vercel
vercel

# Or with specific environment
vercel --prod
```

Configuration in `vercel.json`:
- Builds frontend and copies to output
- Sets up Python serverless function
- Configures routing and rewrites
- Environment variables set in dashboard

### Environment Setup for Deployment
1. Set all required environment variables
2. Ensure Convex deployment is configured
3. Update CORS settings for production domains
4. Configure Clerk for production URLs

## Common Tasks

### Adding a New Page
1. Create component in `frontend/src/pages/`
2. Add route in `App.jsx`
3. Update navigation components
4. Create necessary Convex functions
5. Add any required API endpoints

### Adding a New API Endpoint
1. Define route in `backend/src/api.py`
2. Create Pydantic models if needed
3. Implement business logic
4. Add error handling
5. Update frontend to call new endpoint
6. Update CORS if necessary

### Adding a New Database Table
1. Update `frontend/convex/schema.ts`
2. Create functions in new file (e.g., `frontend/convex/tablename.ts`)
3. Run `npx convex dev` to generate types
4. Use in frontend components
5. Add any backend API integration

### Integrating New AI Features
1. Design prompt structure
2. Update `/chat` endpoint or create new endpoint
3. Handle response parsing
4. Store in Convex if needed
5. Create UI components for interaction
6. Add loading and error states

## Testing

### Unit Tests
- Frontend: Jest + React Testing Library
- Backend: pytest + FastAPI test client

### E2E Tests
```bash
cd tests
npm install
npx playwright test
```

### Manual Testing Checklist
- [ ] Authentication flow (sign up, sign in, sign out)
- [ ] Trip creation and management
- [ ] AI chat functionality
- [ ] Real-time updates (open in multiple tabs)
- [ ] Error handling (network errors, invalid inputs)
- [ ] Responsive design (mobile, tablet, desktop)

## Debugging

### Frontend Debugging
- React DevTools for component inspection
- Network tab for API calls
- Console for Convex queries/mutations
- Vite's error overlay for build errors

### Backend Debugging
- FastAPI's automatic documentation at `/docs`
- Python debugger (`import pdb; pdb.set_trace()`)
- Logging with Python's logging module
- Environment variable verification endpoint

### Convex Debugging
- Convex dashboard for data inspection
- Function logs in Convex dashboard
- `ConvexDebug.jsx` component for testing
- Real-time data explorer

## Performance Optimization

### Frontend
- Lazy load routes with React.lazy()
- Optimize images (WebP, lazy loading)
- Minimize bundle size (analyze with vite-bundle-visualizer)
- Use React.memo for expensive components

### Backend
- Use FastAPI's async endpoints
- Implement caching for AI responses
- Optimize database queries
- Use connection pooling

### Convex
- Design efficient indexes
- Paginate large data sets
- Use reactive queries wisely
- Batch mutations when possible

## Security Considerations

### Authentication
- Always verify Clerk tokens
- Implement proper RBAC
- Secure API endpoints
- Validate all user inputs

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate and sanitize inputs
- Handle errors without exposing internals

### Environment Variables
- Never commit `.env` files
- Use different keys for dev/prod
- Rotate keys regularly
- Limit key permissions

## Best Practices

### Do's
- Keep components small and focused
- Use TypeScript for Convex functions
- Handle loading and error states
- Write descriptive commit messages
- Test edge cases
- Document complex logic

### Don'ts
- Don't store sensitive data in frontend
- Don't make synchronous API calls
- Don't ignore TypeScript errors
- Don't skip error handling
- Don't hardcode configuration
- Don't bypass authentication

## MCP Integration

The project includes MCP (Model Context Protocol) servers for enhanced development:

### Available MCP Servers
1. **Playwright Browser Automation**
   - Browser control and testing
   - Screenshot capabilities
   - Form interaction

2. **Stripe Payment Processing**
   - Customer management
   - Product and pricing
   - Subscription handling

3. **Convex Database**
   - Direct database access
   - Function execution
   - Schema management

### MCP Configuration
See `.mcp.json` and `claude_desktop_config.json` for setup details.

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check backend CORS configuration
   - Verify frontend API URLs
   - Ensure ports match

2. **Authentication Failed**
   - Verify Clerk keys
   - Check user storage in Convex
   - Review auth configuration

3. **Convex Connection Issues**
   - Verify Convex URL
   - Check deployment status
   - Review function implementations

4. **Build Failures**
   - Clear node_modules and reinstall
   - Check for TypeScript errors
   - Verify environment variables

### Getting Help
- Check error messages carefully
- Review Convex and Clerk documentation
- Use debugging tools mentioned above
- Search for similar issues in forums