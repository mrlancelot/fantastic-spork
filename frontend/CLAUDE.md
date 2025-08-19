# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

Waypoint is a modern React + TypeScript travel itinerary planning application with a complete frontend implementation.

## Project Overview

**Waypoint** is a travel itinerary planning app that provides users with an intuitive interface to plan personalized travel experiences. The application features:

- Modern React 18 + TypeScript setup with Vite
- Responsive design with Tailwind CSS
- React Router for navigation
- Mock data for UI demonstration
- AI-powered travel assistant chat interface
- Complete user flow from search to itinerary display

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS with custom primary colors
- **Routing**: React Router DOM v6
- **Icons**: Lucide React
- **Date handling**: date-fns
- **Development**: ESLint, PostCSS, Autoprefixer

## Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation & Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Application Structure

```
src/
├── pages/           # Main application pages
│   ├── LandingPage.tsx      # Homepage with search form
│   ├── LoadingPage.tsx      # Progress/loading screen
│   └── ItineraryPage.tsx    # Final itinerary display
├── components/      # Reusable UI components
│   ├── Header.tsx           # Navigation header
│   ├── SearchForm.tsx       # Travel search form
│   ├── ProgressCard.tsx     # Loading progress display
│   ├── ItineraryCard.tsx    # Daily itinerary card
│   └── TravelAssistant.tsx  # AI chat interface
├── types/          # TypeScript interfaces
├── utils/          # Helper functions (date formatting, etc.)
├── data/           # Mock data for UI demonstration
└── index.css       # Global styles and Tailwind configuration
```

## Key Features

1. **Landing Page** (`/`) - Hero section with comprehensive search form
2. **Loading Page** (`/loading`) - Animated progress tracking with realistic steps
3. **Itinerary Page** (`/itinerary`) - Complete travel plan display with:
   - Daily activity breakdowns
   - Cost calculations
   - Travel tips and weather information
   - Emergency contact information
   - Interactive travel assistant chat

## Design System

- **Primary Color**: Blue (#2563EB)
- **Components**: Card-based layout with consistent spacing
- **Typography**: Inter font family
- **Icons**: Lucide React icon set
- **Responsive**: Mobile-first design approach

## Mock Data

The application includes comprehensive mock data for a Paris trip including:
- Multi-day itinerary with varied activities
- Cost breakdowns and budget tracking
- Realistic activity descriptions and locations
- Progress steps for loading simulation

## Development Notes

- All components are fully typed with TypeScript
- Responsive design tested across device sizes
- Mock travel assistant provides realistic chat interface
- Date utilities handle formatting and calculations
- Modular component architecture for easy maintenance

## Future Enhancements

- Backend API integration
- User authentication
- Real-time travel data
- Payment processing
- Social sharing features
- Offline capability