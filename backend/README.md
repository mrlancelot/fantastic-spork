# TravelAI Backend - Modular Architecture with Web Scrapers

A powerful FastAPI backend for travel planning with web scraping capabilities for flights and hotels, plus AI-powered smart planning.

## 🚀 Overview

This backend provides comprehensive travel services using:
- **Web Scrapers** for real-time flight and hotel data (Google Flights, Booking.com)
- **Tavily API** for restaurant recommendations
- **AI Agents** for intelligent trip planning and orchestration
- **Clean modular architecture** with service layers and proper separation of concerns

## 📁 Project Structure

```
backend/
├── main.py                    # Entry point - runs the API server
├── src/
│   ├── api_server.py         # Main FastAPI application
│   ├── core/                 # Core utilities and scrapers
│   │   ├── config.py         # Centralized configuration
│   │   ├── logger.py         # Colored logging system
│   │   ├── base_scraper.py   # Base scraper class
│   │   ├── google_flights_scraper.py  # Google Flights scraper
│   │   └── booking_scraper.py         # Booking.com scraper
│   ├── agents/               # AI agents
│   │   ├── master_agent.py   # Master orchestration agent
│   │   └── day_planner_agent.py  # Day-by-day planning
│   └── services/             # Service layer
│       ├── flight_service.py     # Flight search service
│       ├── hotel_service.py      # Hotel search service
│       ├── restaurant_service.py # Restaurant service (Tavily)
│       ├── restaurant_agent.py   # Restaurant agent implementation
│       ├── smart_planner.py      # Smart itinerary planning
│       ├── agent_workflow.py     # Agent orchestration
│       ├── market_insights.py    # Market analytics
│       ├── user_service.py       # User management
│       └── utils.py              # Utility functions
├── requirements.txt          # Python dependencies
└── logs/                     # Application logs
```

## ✨ Key Features

### 🔍 Web Scraping Services
- **Google Flights Scraper**: Real-time flight data with multiple options
- **Booking.com Scraper**: Comprehensive hotel search with prices and ratings
- **No API limits**: Scraping bypasses traditional API rate limits

### 🍴 Restaurant Discovery
- **Tavily Integration**: Web search for best restaurants
- **Smart Recommendations**: Cuisine-based and rating-based filtering

### 🤖 AI-Powered Planning
- **Master Agent**: Orchestrates all services with streaming responses
- **Day Planner**: Creates detailed daily itineraries
- **Smart Context**: Understands user preferences and trip context

### 🏗️ Clean Architecture
- **Service Layer Pattern**: Abstraction over scrapers
- **Dependency Injection**: Clean service initialization
- **Comprehensive Logging**: Colored logs for easy debugging
- **Error Handling**: Graceful fallbacks and error recovery

## 🛠️ Tech Stack

- **Framework**: FastAPI with async/await
- **Web Scraping**: Playwright for browser automation
- **AI/LLM**: 
  - Google Gemini for planning
  - OpenRouter for additional AI features
- **Restaurant Data**: Tavily API
- **Data Validation**: Pydantic models
- **Logging**: Custom colored logger

## 📦 Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd fantastic-spork/backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers
```bash
playwright install chromium
```

### 5. Configure environment variables
Create a `.env` file in the project root:
```env
# AI Services
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_key  # Optional

# Restaurant Service
TAVILY_API_KEY=your_tavily_api_key

# Authentication (if using)
CLERK_SECRET_KEY=sk_test_...

# Database (if using Convex)
CONVEX_URL=https://your-deployment.convex.cloud
CONVEX_DEPLOYMENT=production

# Scraper Settings
SCRAPER_HEADLESS=true  # Set to false for debugging
```

## 🚀 Running the Application

### Development Mode
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn src.api_server:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Key API Endpoints

### Flight Search
```http
POST /api/flights/search
{
  "origin": "Kansas City",
  "destination": "Knoxville",
  "departure_date": "2025-08-16",
  "return_date": "2025-08-19",
  "adults": 2,
  "class": "economy"
}
```

### Hotel Search
```http
POST /api/hotels/search
{
  "destination": "Knoxville, Tennessee",
  "check_in": "2025-08-16",
  "check_out": "2025-08-19",
  "adults": 2,
  "rooms": 1
}
```

### Restaurant Search
```http
POST /api/restaurants/search
{
  "destination": "Knoxville, Tennessee",
  "cuisine": "Italian",
  "price_range": "$$"
}
```

### Smart Trip Planning
```http
POST /api/planner/smart
{
  "destination": "Nashville",
  "start_date": "2025-08-10",
  "end_date": "2025-08-13",
  "budget": 2000,
  "preferences": {
    "interests": ["music", "food", "culture"]
  }
}
```

### Master Agent (with streaming)
```http
POST /api/agent/plan
{
  "destination": "Orlando",
  "duration": 3,
  "budget": 1500,
  "interests": ["theme parks", "dining"]
}
```

## 📊 Response Examples

### Flight Search Response
```json
{
  "status": "success",
  "total": 10,
  "flights": [
    {
      "airline": "American",
      "price": 309,
      "price_formatted": "$309",
      "departure_time": "6:00 AM",
      "arrival_time": "11:35 AM",
      "duration": "4h 35m",
      "stops": 1,
      "origin": "MCI",
      "destination": "TYS"
    }
  ],
  "best_price": 309,
  "recommendations": {
    "cheapest": {...},
    "fastest": {...},
    "best_value": {...}
  }
}
```

### Hotel Search Response
```json
{
  "status": "success",
  "total": 26,
  "hotels": [
    {
      "name": "Courtyard by Marriott Knoxville Downtown",
      "price": 184,
      "price_formatted": "$184",
      "rating": 8.5,
      "location": "Downtown Knoxville",
      "amenities": ["WiFi", "Pool", "Gym"]
    }
  ],
  "recommendations": {
    "cheapest": {...},
    "best_rated": {...},
    "best_value": {...}
  }
}
```

## 🎯 Performance Features

- **Concurrent Scraping**: Async architecture for parallel searches
- **Smart Caching**: In-memory caching with TTL
- **Headless Mode**: Faster scraping in production
- **Lazy Loading**: Services initialized only when needed
- **Streaming Responses**: Real-time updates for long operations

## 🔒 Security Considerations

- **CORS**: Currently allows all origins (`*`) - restrict in production
- **API Keys**: All sensitive data in environment variables
- **Rate Limiting**: Implement for production use
- **Error Handling**: No sensitive data in error messages

## 🐛 Troubleshooting

### Common Issues

1. **Scrapers returning 0 results**
   - Check internet connection
   - Try with `SCRAPER_HEADLESS=false` to see browser
   - Verify dates are in future

2. **Playwright browser not found**
   ```bash
   playwright install chromium
   ```

3. **Port already in use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

4. **Tavily API errors**
   - Verify TAVILY_API_KEY is set
   - Check API credits

## 🚀 Deployment

### Docker Deployment
See `Dockerfile` for containerized deployment.

### Vercel Deployment
See `vercel.json` for serverless deployment configuration.

## 📈 Future Enhancements

- [ ] Add more hotel booking sites (Hotels.com, Expedia)
- [ ] Implement flight booking links
- [ ] Add car rental search
- [ ] Implement user authentication
- [ ] Add Redis caching layer
- [ ] Create mobile app API endpoints
- [ ] Add WebSocket support for real-time updates
- [ ] Implement saved searches and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Open a Pull Request

## 📄 License

[Your License Here]

## 💬 Support

For issues or questions:
- Open an issue on GitHub
- Check API documentation at `/docs`

---

**Built with ❤️ for modern travel planning**