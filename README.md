# TravelAI - AI-Powered Travel Planning Platform

A modern full-stack travel planning application that leverages AI to create personalized itineraries and enhance the travel planning experience. Built with React, FastAPI, Convex, and powered by real travel data from Amadeus GDS and Google's Gemini AI.

## Overview

TravelAI is a comprehensive travel planning platform that combines cutting-edge technologies to deliver a seamless experience for travelers. The application uses a smart hybrid architecture that optimizes for both security and performance, ensuring real-time updates while maintaining data integrity.

### Key Highlights

- **AI-Powered Planning**: Chat with Gemini AI assistant to get personalized travel recommendations
- **Smart Itinerary Generation**: Automatically create detailed day-by-day travel plans
- **Trip Management**: Organize and track all your trips in one place with real-time sync
- **Secure Authentication**: Google OAuth and email/password authentication via Clerk
- **Real-time Database**: Powered by Convex for instant data synchronization
- **Destination Discovery**: Explore popular destinations with curated guides
- **User Preferences**: Save your travel style and budget preferences
- **Beautiful UI/UX**: Modern, responsive interface with smooth animations using Framer Motion
- **Smart Architecture**: Hybrid approach - direct Convex reads for performance, backend writes for security

## Features

### 🤖 AI Travel Assistant
- Interactive chat interface powered by Gemini AI
- Personalized recommendations based on your preferences
- Smart itinerary suggestions with time optimization
- Natural language processing for intuitive trip planning
- Context-aware responses for destination-specific advice

### 📅 Trip Dashboard
- View and manage all your trips in a beautiful grid layout
- Real-time updates across devices via Convex
- Quick access to itineraries with one-click navigation
- Trip status tracking (upcoming, ongoing, completed)
- Empty state guidance for new users

### 🗺️ Itinerary Management
- AI-generated day-by-day activity planning
- Visual timeline view with activities and timings
- Save and manage multiple itineraries per trip
- Open, edit, and delete saved itineraries
- Budget tracking and expense management
- Export and share capabilities

### 🌍 Destination Discovery
- Explore 6 popular destinations with stunning imagery
- Interactive destination cards with ratings and pricing
- Filter by travel style (Culture, Beach, Romance, etc.)
- Quick planning integration from destination selection
- Real pricing estimates per day

### 🎯 Trip Planning Interface
- Smart trip form with destination and date selection
- Travel style preferences (Adventure, Relaxation, Culture, Business)
- Budget range configuration
- Number of travelers setting
- Interest tagging system
- AI-powered itinerary generation
- Save multiple itineraries per trip

### 👤 User Profile & Authentication
- Secure authentication with Clerk
- Google OAuth and email/password support
- Automatic user data synchronization
- Profile image and user details management
- Session persistence across devices

### 🎨 Modern UI/UX
- Responsive design for all screen sizes
- Smooth page transitions with Framer Motion
- Toast notifications for user feedback
- Loading states and error handling
- Gradient effects and modern styling
- Custom UI component library

## Tech Stack

### Frontend
- **React 18** - UI framework with hooks for state management
- **Vite** - Lightning-fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Framer Motion** - Production-ready animation library
- **Lucide React** - Modern, tree-shakeable icon library
- **@headlessui/react** - Unstyled, accessible UI components
- **Clerk React** - Authentication and user management
- **Convex React** - Real-time database hooks and providers

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.8+** - Backend runtime
- **Pydantic** - Data validation using Python type annotations
- **Amadeus GDS** - Real-time flight, hotel, and activity data
- **Google Gemini AI** - Advanced AI model for travel recommendations
- **OpenRouter** - Multi-model AI routing
- **Convex Python SDK** - Backend integration with Convex
- **HTTPX** - Async HTTP client for external API calls
- **python-dotenv** - Environment variable management

### Infrastructure
- **Convex** - Real-time database and serverless functions
- **Clerk** - Authentication service with SSO support
- **Vercel** - Deployment platform with edge functions
- **Docker** - Containerization for consistent deployments

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- pip (Python package manager)
- Convex account (free tier available)
- Clerk account (free tier available)
- Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fantastic-spork.git
cd fantastic-spork
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update the `.env` file with your API keys:
```env
# Amadeus GDS (Global Distribution System)
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_SECRET=your_amadeus_secret

# AI Services
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_key

# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

# Convex
VITE_CONVEX_URL=your_convex_url
CONVEX_URL=your_convex_url
CONVEX_DEPLOYMENT=your_convex_deployment
```

3. Set up Convex:
```bash
cd frontend
npx convex dev
```

### Running Locally

#### Option 1: Run all services together (Recommended)
```bash
./run.sh all
```
This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:5173
- Convex real-time database

#### Option 2: Run services separately

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
python -m src.main
```

2. In a new terminal, start the frontend development server:
```bash
cd frontend
npm run dev
```

3. In another terminal, run Convex:
```bash
cd frontend
npx convex dev
```

4. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
fantastic-spork/
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   │   ├── AuthWrapper.jsx
│   │   │   ├── SignInPage.jsx
│   │   │   ├── SignUpPage.jsx
│   │   │   └── TripForm.jsx
│   │   ├── App.jsx        # Main application component
│   │   └── main.jsx       # Application entry point
│   ├── convex/            # Convex backend functions
│   │   ├── schema.ts      # Database schema
│   │   ├── users.ts       # User management functions
│   │   ├── trips.ts       # Trip management functions
│   │   └── chats.ts       # AI chat functions
│   ├── package.json
│   └── vite.config.js
├── backend/               # FastAPI backend application
│   ├── src/
│   │   ├── main.py       # FastAPI app with router architecture
│   │   ├── routers/      # API route modules
│   │   │   ├── flights.py    # Amadeus flight search
│   │   │   ├── hotels.py     # Amadeus hotel search
│   │   │   ├── activities.py # Amadeus activities
│   │   │   ├── analytics.py  # Travel analytics
│   │   │   ├── planner.py    # Smart itinerary planner
│   │   │   ├── chat.py       # AI chat integration
│   │   │   └── health.py     # Health checks
│   │   ├── agents/       # AI agents for planning
│   │   └── services/     # Service integrations
│   └── requirements.txt
├── .env                  # Single environment config
├── run.sh               # Enhanced service runner
├── vercel.json          # Vercel deployment settings
├── CLAUDE.md            # AI assistant instructions
└── README.md
```

## Architecture

The application uses a smart hybrid architecture that optimizes for both security and performance:

### Data Flow Patterns

1. **Read Operations** (Frontend → Convex)
   - Direct queries for real-time updates
   - Automatic caching and synchronization
   - Optimal performance for data fetching

2. **Write Operations** (Frontend → Backend → Convex)
   - Server-side validation and business logic
   - Secure handling of sensitive operations
   - Audit trail capabilities

3. **External APIs** (Frontend → Backend → External Services)
   - API keys stay secure on backend
   - Rate limiting and error handling
   - Response caching when appropriate

This approach ensures optimal performance while maintaining security and control over business logic.

## API Endpoints

### Backend API (FastAPI)

#### Health & Status
- `GET /api/health` - System health check
- `GET /api/status` - Detailed service status

#### Flight Services (Amadeus GDS)
- `GET /api/flights/search` - Search real-time flights
  - Query params: `origin`, `destination`, `departure_date`, `adults`
- `GET /api/flights/status` - Get flight status
  - Query params: `carrier_code`, `flight_number`, `date`
- `GET /api/flights/checkin-links` - Get airline check-in URLs
  - Query params: `airline_code`

#### Hotel Services (Amadeus GDS)
- `GET /api/hotels/search-by-city` - Search hotels by city
  - Query params: `city_code`
- `GET /api/hotels/search` - Search hotels with details
  - Query params: `hotel_ids`
- `GET /api/hotels/sentiments` - Get hotel reviews sentiment
  - Query params: `hotel_ids`

#### Activity Services (Amadeus GDS)
- `GET /api/activities/search` - Search activities by location
  - Query params: `latitude`, `longitude`
- `GET /api/activities/search-by-square` - Search in area
  - Query params: `north`, `south`, `east`, `west`

#### Travel Analytics
- `GET /api/analytics/market-insights` - Get market insights
- `POST /api/analytics/flight-price-analysis` - Analyze flight prices
- `POST /api/analytics/trip-purpose-prediction` - Predict trip purpose
- `GET /api/analytics/travel-recommendations` - Get AI recommendations

#### Smart Planning
- `POST /api/planner/create-itinerary` - Generate smart itinerary
  - Request: `{ "destination": "string", "days": number, "preferences": object }`
- `GET /api/planner/suggestions` - Get destination suggestions

#### AI Chat
- `POST /api/chat` - Chat with AI travel assistant
  - Request: `{ "message": "string" }`
  - Response: `{ "response": "string" }`

### Convex Functions

**Queries (Direct Frontend Access)**
- `users.getMyUser` - Get current authenticated user
- `trips.getUserTrips` - Get all trips for current user
- `trips.getTrip` - Get specific trip by ID
- `itineraries.getByTripId` - Get all itineraries for a trip
- `itineraries.get` - Get specific itinerary by ID

**Mutations (Backend Access Only)**
- `users.storeFromBackend` - Store/update user data
- `trips.createFromBackend` - Create new trip
- `trips.updateFromBackend` - Update existing trip
- `trips.deleteFromBackend` - Delete trip
- `itineraries.createFromBackend` - Save generated itinerary
- `itineraries.deleteFromBackend` - Delete saved itinerary

**Actions**
- `chats.sendMessage` - Send message to AI assistant

## Authentication Flow

1. User signs in with Clerk (Google OAuth or email/password)
2. Frontend detects authentication
3. Frontend calls backend API to store user in Convex
4. Backend uses Convex SDK to store user data
5. User can now access all features

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variables in Vercel dashboard

### Docker Deployment

```bash
docker build -t travelai .
docker run -p 8000:8000 --env-file .env travelai
```

## Testing

Run Playwright E2E tests:
```bash
cd tests
npm install
npx playwright test
```

## MCP Servers

This project includes configuration for Model Context Protocol (MCP) servers:

### Convex MCP
Provides direct access to Convex database operations and functions.

### Context7 MCP
Upstash Context7 for enhanced context management and caching.

To use these MCP servers:
1. Ensure your IDE supports MCP (Cursor, Windsurf, Claude Desktop)
2. The `.mcp.json` file in the root directory contains the configuration
3. For Claude Desktop, use the `claude_desktop_config.json` file

## Database Schema

### Users Table
- `clerkId` - Unique Clerk user ID
- `email` - User email address
- `name`, `firstName`, `lastName` - User name fields
- `imageUrl` - Profile picture URL
- `createdAt`, `updatedAt` - Timestamps

### Trips Table
- `userId` - Reference to user
- `destination` - Trip destination
- `startDate`, `endDate` - Trip dates
- `budget` - Optional budget amount
- `travelers` - Number of travelers
- `activities` - Array of planned activities
- `notes` - Optional trip notes

### Itineraries Table
- `tripId` - Reference to trip
- `userId` - Reference to user
- `day` - Day number of trip
- `activities` - Array of daily activities with time, title, description, location

### Chats Table
- `userId` - Reference to user
- `tripId` - Optional reference to trip
- `messages` - Array of chat messages with role, content, timestamp

## Performance Optimizations

- **Real-time Updates**: Convex subscriptions provide instant data updates
- **Optimistic Updates**: UI updates immediately while backend processes
- **Code Splitting**: Vite automatically splits code for faster loading
- **Image Optimization**: External images loaded from optimized sources
- **Minimal Re-renders**: React hooks and memoization prevent unnecessary updates

## Security Considerations

- **API Keys**: All sensitive keys stored in backend environment only
- **Authentication**: Clerk handles secure auth with industry standards
- **Data Validation**: Pydantic models ensure type safety
- **CORS Configuration**: Restricted to specific origins
- **Backend Validation**: All writes go through backend for validation

## Troubleshooting

### Common Issues

1. **Convex Connection Failed**
   - Check CONVEX_URL in environment variables
   - Ensure `npx convex dev` is running
   - Verify Convex deployment status

2. **Gemini API Errors**
   - Verify GEMINI_API_KEY is set correctly
   - Check API quota limits
   - Ensure internet connectivity

3. **Authentication Issues**
   - Verify Clerk keys are correct
   - Check allowed callback URLs in Clerk dashboard
   - Clear browser cookies and try again

4. **Backend Connection Failed**
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify environment variables are loaded

## Recent Updates

### Backend Architecture Refactoring ✅
- ✅ Complete integration with Amadeus GDS for real travel data
- ✅ Removed all mock data and fallback implementations
- ✅ Refactored to clean router-based architecture
- ✅ Consolidated 8 environment files into single `.env`
- ✅ Enhanced `run.sh` to manage all services (frontend, backend, Convex)

### Features
- ✅ Real-time flight search and booking via Amadeus
- ✅ Hotel search with sentiment analysis
- ✅ Activity recommendations by location
- ✅ AI-powered itinerary generation with Gemini
- ✅ Smart travel analytics and insights
- ✅ Multi-model AI support (Gemini, OpenRouter)
- ✅ Save and manage multiple itineraries per trip
- ✅ Complete trip CRUD operations
- ✅ Real-time database synchronization
- ✅ Beautiful, responsive UI with Framer Motion

## Future Enhancements

- [ ] Mobile app with React Native
- [ ] More AI providers (OpenAI, Anthropic)
- [ ] Collaborative trip planning
- [ ] Booking integration (flights, hotels)
- [ ] Offline mode support
- [ ] Multi-language support
- [ ] Advanced budget tracking
- [ ] Weather integration
- [ ] Photo gallery for trips
- [ ] Social sharing features
- [ ] PDF export for itineraries
- [ ] Calendar sync (Google, Apple)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with modern web technologies
- Powered by Google Gemini AI
- Real-time sync by Convex
- Authentication by Clerk
- UI components inspired by modern design systems