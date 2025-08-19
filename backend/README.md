# Waypoint Backend API

🚀 **Comprehensive Travel API Platform** powered by Amadeus, AI agents, and custom integrations.

## Overview

A production-ready FastAPI backend service providing 30+ travel APIs including flight search, hotel booking, activity discovery, market analytics, and AI-powered travel intelligence. Built with modern async Python and integrated with Amadeus Self-Service APIs.

## 🌟 Key Features

### ✈️ **Flight Services** 
- **Smart Search & Booking**: Multi-airport resolution, deduplication, price optimization
- **Flexible Date Search**: Find cheapest travel dates across a month
- **Flight Operations**: Real-time status tracking, airline check-in links
- **Price Analytics**: Historical pricing data and trends
- **Delay Predictions**: ML-powered delay probability analysis
- **Inspiration Search**: "Where can I go for $500?"

### 🏨 **Hotels**
- **Search & Booking**: Find accommodations by city or coordinates
- **Sentiment Analysis**: Guest review sentiment scoring
- **Price Comparison**: Multi-property price analysis

### 🎯 **Activities & Tours**
- **Experience Discovery**: Find tours and activities by location
- **Real-time Availability**: Live booking status
- **Price Filtering**: Budget-based activity search

### 🚗 **Ground Transportation**
- **Airport Transfers**: Private, shared, and taxi options
- **Route Planning**: Point-to-point transfer search
- **Price Comparison**: Multiple provider options

### 📊 **Market Intelligence**
- **Travel Analytics**: Most traveled/booked destinations
- **Busiest Periods**: Peak travel time analysis
- **Airport Routes**: All destinations from any airport
- **Trip Intelligence**: Business vs leisure trip prediction

### 🤖 **AI Capabilities**
- **Dynamic Data Resolution**: AI-powered airport/airline lookups via OpenRouter
- **No Static Files**: All data resolved in real-time using GPT-4o-mini
- **Intelligent Agents**: Workflow orchestration for complex queries
- **Restaurant Discovery**: Tavily-powered restaurant search

## 📋 API Categories

The API is organized into 15 logical categories in Swagger UI:

1. **Flights - Search & Booking** (5 endpoints)
2. **Flights - Operations** (2 endpoints)
3. **Flights - Analytics** (1 endpoint)
4. **Flights - Predictions** (1 endpoint)
5. **Flights - Inspiration & Planning** (1 endpoint)
6. **Hotels** (3 endpoints)
7. **Activities & Tours** (2 endpoints)
8. **Transfers & Ground Transport** (1 endpoint)
9. **Airports** (1 endpoint)
10. **Market Analytics** (3 endpoints)
11. **Trip Intelligence** (1 endpoint)
12. **Restaurants** (1 endpoint)
13. **AI Agents** (3 endpoints)
14. **System** (2 endpoints)

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115.6 with async/await
- **AI/LLM Integration**: 
  - OpenRouter (GPT-4o-mini) for dynamic lookups
  - LlamaIndex for agent orchestration
  - Google Gemini for fallback
- **Travel Data**: Amadeus Self-Service APIs (v12.0.0)
- **Data Validation**: Pydantic v2 models
- **HTTP Client**: aiohttp for async requests
- **Environment**: Python 3.8+

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/waypoint-be.git
cd waypoint-be
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

### 4. Install Playwright browsers (for flight_search.py)
```bash
playwright install chromium
```

### 5. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your API credentials:
```env
# Amadeus API (Required for travel services)
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_Secret=your_amadeus_secret

# OpenRouter (Required for AI lookups)
OPENROUTER_API_KEY=your_openrouter_key

# Optional Services
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key
BRIGHT_DATA_API_TOKEN=your_bright_data_token
TAVILY_API_KEY=your_tavily_api_key
```

## 🚀 Running the Application

### Development Mode
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs (Organized by categories)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔑 Key API Endpoints

### Flight Search
```http
POST /flights/search
{
  "origin": "NYC",
  "destination": "LON",
  "departure_date": "2025-06-01",
  "return_date": "2025-06-08",
  "adults": 2
}
```

### Cheapest Dates
```http
GET /flights/cheapest-dates?origin=NYC&destination=PAR&duration=7
```

### Flight Status
```http
GET /flights/status?carrier_code=AA&flight_number=100&scheduled_departure_date=2025-12-01
```

### Hotel Search
```http
GET /hotels/search?city_code=PAR&check_in_date=2025-03-15&check_out_date=2025-03-18&adults=2
```

### Activities
```http
GET /activities/search?latitude=48.8566&longitude=2.3522&radius=5
```

### Flight Inspiration
```http
GET /flights/inspiration?origin=NYC&max_price=500
```

### Market Analytics
```http
GET /analytics/most-traveled?origin_city_code=NYC&period=2025-06
```

### Trip Purpose Prediction
```http
GET /trips/purpose-prediction?origin=NYC&destination=SFO&departure_date=2025-06-01&return_date=2025-06-03
```

## 📁 Project Structure

```
waypoint-be/
├── main.py                      # FastAPI application & endpoints
├── agent.py                     # AI agent configurations
├── requirements.txt             # Python dependencies
├── CLAUDE.md                   # Development instructions for Claude
├── .env                        # Environment variables
├── agents/
│   ├── flights.py              # Amadeus flight search implementation
│   ├── travel_services.py      # Hotels, Activities, Transfers, Status
│   ├── market_insights.py      # Analytics and predictions
│   ├── flight_search.py        # Alternative Playwright-based search
│   ├── restaurant_agent.py     # Restaurant discovery
│   ├── hotel_agent.py         # Hotel search agent
│   ├── flight_agent.py        # Legacy flight agent
│   └── itinerary_writer.py    # Itinerary writing orchestration
└── service/
    └── exceptions.py           # Custom exception hierarchy
```

## 🏗️ Architecture

### Service Layer Architecture
```
┌─────────────────────────────────────────────┐
│              FastAPI Application             │
├─────────────────────────────────────────────┤
│                API Endpoints                 │
│  (Organized by Tags: Flights, Hotels, etc)  │
├─────────────────────────────────────────────┤
│             Service Classes                  │
│  ┌─────────────┐ ┌──────────────┐          │
│  │AmadeusFligh│ │HotelSearchSer│          │
│  │tService    │ │vice          │          │
│  └─────────────┘ └──────────────┘          │
├─────────────────────────────────────────────┤
│           AI Lookup Service                  │
│      (OpenRouter GPT-4o-mini)               │
├─────────────────────────────────────────────┤
│          External APIs                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Amadeus  │ │OpenRouter│ │  Tavily  │   │
│  │   APIs   │ │    AI    │ │   MCP    │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
```

### Key Design Patterns

1. **Dynamic Resolution**: No static JSON files - all data resolved via AI
2. **Async/Await**: Full async support for high performance
3. **Service Classes**: Encapsulated business logic per domain
4. **Pydantic Models**: Type-safe request/response validation
5. **Error Handling**: Custom exception hierarchy with graceful fallbacks

## 🧪 Test Environment Limitations

Currently using Amadeus **TEST** environment with these limitations:
- Limited data availability for some endpoints
- Historical data restrictions (no past dates for some APIs)
- Hotel search API not fully available
- Transfer search has limited test data
- Free monthly quotas per API endpoint

## 🔒 Security Considerations

- **CORS**: Currently allows all origins (`*`) - restrict in production
- **Authentication**: No auth implemented - add JWT/OAuth for production
- **Rate Limiting**: Not implemented - add for production
- **Secrets**: All sensitive data in environment variables
- **HTTPS**: Use reverse proxy (nginx/caddy) in production

## 📈 Performance

- **Concurrent Requests**: Async architecture supports high concurrency
- **Response Times**: <500ms for most endpoints
- **AI Lookups**: Cached where possible to reduce latency
- **Database**: Currently in-memory - add PostgreSQL/MongoDB for production

## 🎯 Future Enhancements

- [ ] Add PostgreSQL database for persistence
- [ ] Implement user authentication (JWT/OAuth)
- [ ] Add Redis caching layer
- [ ] Implement WebSocket support for real-time updates
- [ ] Add rate limiting and API key management
- [ ] Create mobile app SDKs (iOS/Android)
- [ ] Add GraphQL endpoint option
- [ ] Implement booking confirmation emails
- [ ] Add payment gateway integration
- [ ] Create admin dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Response Examples

### Flight Search Response
```json
{
  "origin_code": "JFK",
  "destination_code": "LHR",
  "departure_date": "2025-06-01",
  "return_date": "2025-06-08",
  "current_price": "$456",
  "outbound_flights": [
    {
      "airline": "American Airlines",
      "departure_time": "19:00",
      "arrival_time": "06:50",
      "duration": "6h 50m",
      "stops": 0,
      "price": "$456",
      "booking_url": "https://www.aa.com/..."
    }
  ],
  "total_flights": 20
}
```

### Market Analytics Response
```json
{
  "origin": "NYC",
  "period": "2025-06",
  "destinations": [
    {
      "destination": "LAX",
      "destination_name": "Los Angeles",
      "travelers": 15420,
      "percentage": 12.5
    }
  ],
  "total_travelers": 123360
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Amadeus 400 Errors**: Check date formats (YYYY-MM-DD) and ensure future dates
2. **AI Lookup Failures**: Verify OpenRouter API key and credits
3. **Hotel Search Not Working**: Limited in test environment - use production credentials
4. **Port Already in Use**: Kill existing process: `lsof -ti:8000 | xargs kill -9`

## 📄 License

[Add your license here]

## 💬 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review API documentation at `/docs`

## 🙏 Acknowledgments

- Amadeus for Self-Service APIs
- OpenRouter for AI infrastructure
- FastAPI community for excellent framework
- All contributors and testers

---

**Built with ❤️ for modern travel applications**