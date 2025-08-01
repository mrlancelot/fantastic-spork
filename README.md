# TravelAI - AI-Powered Travel Planning Platform

A full-stack web application that uses AI to create personalized travel itineraries, built with React, FastAPI, Convex, and Clerk Authentication.

## Overview

TravelAI is an intelligent travel planning platform that helps users create personalized itineraries with the help of AI. The application features:

- **AI-Powered Planning**: Chat with Gemini AI assistant to get personalized travel recommendations
- **Smart Itinerary Generation**: Automatically create detailed day-by-day travel plans
- **Trip Management**: Organize and track all your trips in one place with real-time sync
- **Secure Authentication**: Google OAuth and email/password authentication via Clerk
- **Real-time Database**: Powered by Convex for instant data synchronization
- **Destination Discovery**: Explore popular destinations with curated guides
- **User Preferences**: Save your travel style and budget preferences

## Features

### 🤖 AI Travel Assistant
- Interactive chat interface powered by Gemini AI
- Personalized recommendations based on your preferences
- Smart itinerary suggestions with time optimization

### 📅 Trip Dashboard
- View and manage all your trips
- Real-time updates across devices
- Quick access to itineraries
- Trip status tracking (upcoming, ongoing, completed)

### 🗺️ Itinerary Builder
- Day-by-day activity planning
- Integrated booking links
- Budget tracking
- Export and share capabilities

### 🌍 Destination Guide
- Explore popular destinations
- View top attractions with ratings
- Get practical travel tips
- Budget estimates and best travel times

### 👤 User Profile
- Secure authentication with Clerk
- Save travel preferences
- Manage notification settings
- Track favorite destinations

## Tech Stack

### Frontend
- **React 18** - UI framework with hooks for state management
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Lucide React** - Modern icon library
- **Clerk** - Authentication and user management
- **Convex** - Real-time database and backend functions

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.8+** - Backend runtime
- **Pydantic** - Data validation using Python type annotations
- **Gemini AI** - Google's AI model for travel recommendations
- **Convex Python SDK** - Backend integration with Convex

### Infrastructure
- **Convex** - Real-time database and serverless functions
- **Clerk** - Authentication service
- **Vercel** - Deployment platform

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
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

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

#### Option 1: Run both services together
```bash
./run.sh both
```

#### Option 2: Run services separately

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
fastapi dev src/api.py
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
│   │   ├── api.py        # API routes and endpoints
│   │   └── main.py       # Server configuration
│   └── requirements.txt
├── api/                  # Vercel deployment configuration
├── tests/                # Playwright E2E tests
├── run.sh               # Utility script to run services
├── vercel.json          # Vercel deployment settings
├── CLAUDE.md            # AI assistant instructions
└── README.md
```

## API Endpoints

### Backend API
- `GET /hello` - Health check
- `POST /chat` - Chat with Gemini AI
- `POST /store-user` - Store user in Convex (called by frontend)
- `GET /test-env` - Test environment variables

### Convex Functions
- `users.store` - Store authenticated user
- `users.storeFromBackend` - Store user via backend API
- `users.getMyUser` - Get current user data
- `trips.create` - Create a new trip
- `trips.getUserTrips` - Get user's trips
- `chats.sendMessage` - Send message to AI

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.