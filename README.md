# TravelAI - AI-Powered Travel Planning Platform

A full-stack web application that uses AI to create personalized travel itineraries, built with React and FastAPI.

## Overview

TravelAI is an intelligent travel planning platform that helps users create personalized itineraries with the help of AI. The application features:

- **AI-Powered Planning**: Chat with an AI assistant to get personalized travel recommendations
- **Smart Itinerary Generation**: Automatically create detailed day-by-day travel plans
- **Trip Management**: Organize and track all your trips in one place
- **Destination Discovery**: Explore popular destinations with curated guides
- **Real-time Booking**: Direct links to book flights, hotels, and activities
- **User Preferences**: Save your travel style and budget preferences

## Features

### 🤖 AI Travel Assistant
- Interactive chat interface for travel planning
- Personalized recommendations based on your preferences
- Smart itinerary suggestions with time optimization

### 📅 Trip Dashboard
- View upcoming and past trips
- Quick access to itineraries
- Trip status tracking

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
- Save travel preferences
- Manage notification settings
- Track favorite destinations
- Payment method management

## Tech Stack

### Frontend
- **React** - UI framework with hooks for state management
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Lucide React** - Modern icon library
- **Vite** - Fast build tool and development server

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.8+** - Backend runtime
- **Pydantic** - Data validation using Python type annotations

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travelai.git
cd travelai
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
pip install -r requirements.txt
```

### Running Locally

1. Start the backend server:
```bash
cd backend
fastapi dev src/api.py
```

2. In a new terminal, start the frontend development server:
```bash
cd frontend
npm run dev
```


3. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
travelai/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── App.jsx    # Main application component
│   │   └── main.jsx   # Application entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/           # FastAPI backend application
│   ├── src/
│   │   ├── api.py    # API routes and endpoints
│   │   └── main.py   # Server configuration
│   └── requirements.txt
├── api/              # Vercel deployment configuration
├── vercel.json       # Vercel settings
└── README.md
```

## Deployment

This application can be deployed on:
- **Vercel** - For serverless deployment
- **Render** - For containerized deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
