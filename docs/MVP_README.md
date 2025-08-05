# Waypoint - AI Travel Planner MVP

A 2-page React frontend for AI-powered travel planning with local insights.

## 🚀 Quick Start

### Option 1: Run Both Frontend & Backend Together
```bash
./run.sh both
```

### Option 2: Run Separately
```bash
# Terminal 1 - Backend (http://localhost:8000)
./run.sh backend

# Terminal 2 - Frontend (http://localhost:5173) 
./run.sh frontend
```

## 📱 Pages Overview

### 1. Landing Page (/)
**Route:** `/`  
**Component:** `Landing.jsx`

**Features:**
- Hero section with "Waypoint - AI Travel Planner for Locals" branding
- Travel planning form with pre-filled demo data:
  - Destination: "Buenos Aires and Patagonia"
  - Travel dates: "November 2024" 
  - Number of travelers: 6
  - Departure cities: Checkboxes for San Francisco, NYC, LA, Shanghai
- Blue gradient background with white card design
- Mobile responsive layout
- Form data stored in localStorage
- Navigates to `/itinerary` on submit

### 2. Itinerary Page (/itinerary)
**Route:** `/itinerary`  
**Component:** `Itinerary.jsx`

**Features:**
- Retrieves form data from localStorage
- Shows loading spinner while generating itinerary
- Calls `POST http://localhost:8000/api/generate-itinerary` on page load
- Displays structured itinerary with sections:
  - **Trip Summary**: Overview of the planned trip
  - **Flights**: Airlines, prices, and booking links for all departure cities
  - **Accommodations**: Hotels/Airbnb with neighborhoods and pricing
  - **Food & Dining**: Restaurant recommendations with cuisine types
  - **Activities**: Sightseeing, nightlife, and adventure options
  - **Daily Schedule**: Day-by-day itinerary breakdown
  - **Sources & References**: All URLs used for recommendations
- Each recommendation includes source links for credibility
- Save itinerary button (calls `POST /api/save-itinerary`)
- Mobile responsive with clean card-based layout

## 🛠 Technical Stack

### Frontend
- **React 18** with functional components and hooks
- **React Router DOM** for routing
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons
- **Vite** for development and building

### Backend
- **FastAPI** for API endpoints
- **Perplexity API** for AI-powered itinerary generation
- **Python 3.13** with virtual environment
- **CORS middleware** for cross-origin requests

### Key Dependencies
```json
{
  "react": "^18.3.1",
  "react-router-dom": "^7.7.1", 
  "framer-motion": "^12.23.12",
  "lucide-react": "^0.344.0"
}
```

## 🔌 API Endpoints

### Backend (FastAPI - Port 8000)

#### Health Check
```http
GET /api/health
```
Returns service status

#### Store User (from Clerk Auth)
```http
POST /api/store-user
Content-Type: application/json

{
  "clerk_user_id": "user_xxxx",
  "email": "user@example.com",
  "name": "John Doe",
  "image_url": "https://..."
}
```

#### Generate Itinerary with Booking Links
```http
POST /api/generate-itinerary
Content-Type: application/json

{
  "destination": "Buenos Aires and Patagonia",
  "dates": "November 2024", 
  "travelers": 6,
  "departure_cities": ["San Francisco", "NYC"],
  "trip_type": "group travel"
}
```

**Enhanced Response with Booking Options:**
```json
{
  "itinerary": {
    "flights": [{
      "from": "San Francisco",
      "airline": "United Airlines",
      "booking_options": [
        {
          "platform": "Google Flights",
          "url": "https://www.google.com/flights/...",
          "price_range": "$800-1200",
          "notes": "Direct booking available"
        },
        {
          "platform": "Airline Direct",
          "url": "https://united.com/booking",
          "price_range": "$750-1150",
          "notes": "Official airline site"
        }
      ]
    }],
    "accommodations": [{
      "name": "Hotel Madero",
      "neighborhood": "Puerto Madero",
      "bachelor_friendly": true,
      "booking_options": [
        {
          "platform": "Booking.com",
          "url": "https://booking.com/hotel/...",
          "price_per_night": "$180-250",
          "notes": "Group discounts available"
        },
        {
          "platform": "Direct Hotel",
          "url": "https://hotelmadero.com",
          "price_per_night": "$160-230",
          "contact": "+54-11-5776-7777",
          "notes": "Call for group rates"
        }
      ]
    }],
    "food": [{
      "name": "Don Julio",
      "cuisine": "Steakhouse",
      "good_for_groups": true,
      "booking_options": [
        {
          "platform": "WhatsApp",
          "contact": "+54-11-4831-9564",
          "price_range": "$40-80 per person",
          "notes": "Message for group reservations"
        }
      ]
    }],
    "activities": [{
      "name": "Tango Show at Café Tortoni",
      "type": "nightlife",
      "bachelor_appropriate": true,
      "booking_options": [
        {
          "platform": "Viator",
          "url": "https://viator.com/tours/...",
          "price_per_person": "$45-85",
          "notes": "Skip-the-line tickets included"
        }
      ]
    }],
    "schedule": {
      "day1": ["Airport arrival", "Check-in at hotel", "Welcome dinner"],
      "day2": ["City tour", "Lunch at parrilla", "Tango show"],
      "day3": ["Fly to Patagonia", "Glacier tour", "Farewell dinner"]
    },
    "booking_summary": {
      "total_estimated_cost": "$2500-4000 per person",
      "best_booking_strategy": "Book flights first, then accommodations",
      "group_booking_tips": [
        "Contact hotels directly for group rates",
        "Make restaurant reservations 2-3 weeks ahead",
        "Book activities with free cancellation"
      ]
    }
  },
  "booking_validation": {
    "has_flight_bookings": true,
    "has_hotel_bookings": true,
    "has_restaurant_bookings": true,
    "has_activity_bookings": true
  },
  "status": "success"
}
```

#### Save Itinerary to Convex
```http
POST /api/save-itinerary
Content-Type: application/json

{
  "itinerary_data": {
    "destination": "Buenos Aires and Patagonia",
    "dates": "November 2024",
    "travelers": 6,
    "departureCities": ["San Francisco", "NYC"],
    "itinerary": {...},
    "booking_validation": {...}
  },
  "user_id": "user_xxxx"
}
```

#### Test Booking Search (Development)
```http
POST /api/test-booking-search
Content-Type: application/json

{
  "search_type": "flights",
  "destination": "Buenos Aires",
  "specific_query": "San Francisco",
  "dates": "November 2024",
  "travelers": 6
}
```

### Convex Functions (Real-time Database)

#### User Functions
- `users.getMyUser` - Get current authenticated user
- `users.storeFromBackend` - Store user from Clerk (backend only)

#### Trip Functions
- `trips.getUserTrips` - Get all trips for current user
- `trips.getTrip` - Get specific trip by ID
- `trips.deleteTrip` - Delete a trip (with cascade delete)
- `trips.createFromBackend` - Create trip with full itinerary (backend only)
- `trips.updateFromBackend` - Update trip (backend only)
- `trips.deleteFromBackend` - Delete trip (backend only)

## 🎨 UI/UX Features

### Design System
- **Blue gradient backgrounds** (`from-blue-50 to-blue-100`)
- **White cards** with subtle shadows for content
- **Rounded corners** (xl: 12px) for modern look
- **Consistent spacing** using Tailwind's spacing scale
- **Typography hierarchy** with proper font weights and sizes

### Responsive Design
- **Mobile-first approach** with responsive breakpoints
- **Grid layouts** that adapt to screen size
- **Touch-friendly buttons** and form elements
- **Optimized for both desktop and mobile**

### Loading States
- **Animated spinner** with rotating loader icon
- **Loading messages** to keep users engaged
- **Error handling** with user-friendly messages
- **Progressive disclosure** of content

### Animations
- **Framer Motion** for smooth page transitions
- **Staggered animations** for list items
- **Hover effects** on interactive elements
- **Loading state transitions**

## 🔧 Development Setup

### Prerequisites
- Node.js 18+ 
- Python 3.13+
- Perplexity API key (set as `PERPLEXITY_API_KEY` in backend/.env)

### Installation
```bash
# Frontend dependencies
cd frontend
npm install

# Backend dependencies  
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
Create `backend/.env`:
```env
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

## 📂 Project Structure

```
fantastic-spork/
├── frontend/                    # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Landing.jsx      # Landing page component
│   │   │   ├── Itinerary.jsx    # Itinerary page component  
│   │   │   └── ui/              # Reusable UI components
│   │   ├── App.jsx              # React Router setup
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Tailwind CSS
│   └── package.json
├── backend/                     # FastAPI application
│   ├── src/
│   │   └── api.py              # API routes
│   ├── requirements.txt
│   └── venv/                   # Python virtual environment
├── run.sh                      # Development helper script
└── MVP_README.md              # This file
```

## 🚦 Usage Flow

### For New Users
1. **Visit Landing Page** - See hero section and travel form
2. **Sign Up/Sign In** - Create account via Clerk auth
3. **Fill Travel Form** - Destination, dates, travelers, departure cities
4. **Generate Itinerary** - AI creates personalized travel plan
5. **Review Booking Options** - Multiple platforms per item
6. **Save Itinerary** - Store to personal trip collection

### For Returning Users
1. **Sign In** - Access saved trips dashboard
2. **View Saved Trips** - Grid view with trip cards
3. **Trip Actions**:
   - **Open** - View full itinerary with booking links
   - **Edit** - Modify trip details and regenerate
   - **Delete** - Remove trip with confirmation
4. **Plan New Trip** - Create additional itineraries

### Booking Flow
1. **Review Options** - Each item has multiple booking platforms
2. **Click Booking Button** - Opens platform in new tab
3. **Alternative Contact** - WhatsApp/phone for local businesses
4. **Track Progress** - Visual indicators for booking status

## 🌟 Key Features

### ✅ Implemented
- [x] 2-page React frontend with routing
- [x] Landing page with travel planning form
- [x] Pre-filled demo data (Buenos Aires & Patagonia, Nov 2024, 6 travelers)
- [x] Multiple departure city selection (SF, NYC, LA, Shanghai)
- [x] localStorage for form data persistence
- [x] Itinerary generation with Perplexity AI
- [x] Structured itinerary display (flights, hotels, food, activities)
- [x] Source links for credibility
- [x] Mobile responsive design
- [x] Loading states and error handling
- [x] Save itinerary functionality
- [x] Clean, minimal UI with blue gradient theme

### 🎯 MVP Scope
- **No authentication required** - immediate usability
- **Demo data pre-filled** - showcases functionality
- **Source attribution** - builds user trust
- **Mobile responsive** - works on all devices
- **Fast loading** - optimized for performance

## 🔧 Customization

### Adding New Departure Cities
Edit the `departureCityOptions` array in `Landing.jsx`:
```jsx
const departureCityOptions = [
  'San Francisco',
  'NYC', 
  'LA',
  'Shanghai',
  'Your New City' // Add here
];
```

### Modifying Pre-filled Data
Update the initial `formData` state in `Landing.jsx`:
```jsx
const [formData, setFormData] = useState({
  destination: 'Your Destination',
  dates: 'Your Dates',
  travelers: 4,
  departureCities: ['Your City']
});
```

### Styling Customization  
All styles use Tailwind CSS classes. Key theme colors:
- Primary blue: `blue-600`, `blue-700`
- Background gradient: `from-blue-50 to-blue-100`
- Card backgrounds: `bg-white`
- Text colors: `text-gray-900`, `text-gray-600`

## 🔧 Development Setup

### Prerequisites
- Node.js 18+ 
- Python 3.13+
- Clerk account (for authentication)
- Convex account (for database)
- Perplexity API key (for AI generation)

### Installation
```bash
# Clone repository
git clone <repo-url>
cd fantastic-spork

# Frontend setup
cd frontend
npm install

# Backend setup  
cd ../backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

#### Frontend (.env.local)
```env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_CONVEX_URL=https://...convex.cloud
```

#### Backend (.env)
```env
PERPLEXITY_API_KEY=pplx-...
CLERK_SECRET_KEY=sk_test_...
CONVEX_URL=https://...convex.cloud
CONVEX_DEPLOYMENT=production
```

### Convex Setup
```bash
cd frontend
npx convex dev  # Development
npx convex deploy  # Production
```

## 🐛 Troubleshooting

### Frontend Issues
- **Port 5173 already in use**: Kill existing Vite process or use different port
- **Components not found**: Check import paths in components
- **Routing not working**: Ensure React Router DOM is installed

### Backend Issues  
- **Port 8000 already in use**: Kill existing FastAPI process
- **PERPLEXITY_API_KEY error**: Set environment variable in backend/.env
- **CORS errors**: Check allowed origins in api.py CORS middleware

### API Integration
- **Network request failed**: Ensure backend is running on port 8000
- **Timeout errors**: Perplexity API can be slow, increase timeout if needed
- **JSON parsing errors**: API response format may vary, check error handling

## 📈 Performance Optimizations

- **Code splitting**: React lazy loading for components
- **Image optimization**: Use appropriate formats and sizes  
- **Bundle size**: Tree shaking removes unused code
- **API caching**: Consider caching itinerary responses
- **Loading states**: Keep users engaged during API calls

## 🔒 Security Considerations

- **API keys**: Never expose in frontend, keep in backend environment
- **Input validation**: Sanitize user inputs before API calls
- **CORS policy**: Restrict allowed origins in production
- **Rate limiting**: Implement on API endpoints if needed

---

**Built with ❤️ for rapid MVP development and user testing**