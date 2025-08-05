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

#### Generate Itinerary
```http
POST http://localhost:8000/api/generate-itinerary
Content-Type: application/json

{
  "destination": "Buenos Aires and Patagonia",
  "dates": "November 2024", 
  "travelers": 6,
  "departure_cities": ["San Francisco", "NYC"],
  "trip_type": "group travel"
}
```

**Response:**
```json
{
  "itinerary": {
    "flights": [{"from": "...", "airline": "...", "price_range": "...", "source_url": "..."}],
    "accommodations": [{"name": "...", "neighborhood": "...", "price_per_night": "...", "source_url": "..."}],
    "food": [{"name": "...", "cuisine": "...", "price_range": "...", "source_url": "..."}],
    "activities": [{"name": "...", "type": "...", "source_url": "..."}],
    "schedule": {"day1": ["...", "...", "..."], "day2": ["...", "...", "..."]},
    "sources": ["url1", "url2", "url3"]
  },
  "sources": ["url1", "url2", "url3"],
  "status": "success"
}
```

#### Save Itinerary
```http
POST http://localhost:8000/api/save-itinerary
Content-Type: application/json

{
  "itinerary_data": {...},
  "user_id": "demo-user"
}
```

**Response:**
```json
{
  "success": true,
  "trip_id": "uuid-string",
  "message": "Itinerary saved successfully!"
}
```

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

1. **User visits landing page** (`/`)
2. **Sees pre-filled form** with demo data for Buenos Aires trip
3. **Can modify** destination, dates, travelers, departure cities
4. **Clicks "Generate My Itinerary"** button
5. **Form data saved** to localStorage
6. **Navigates to** `/itinerary` page
7. **Loading spinner** appears while API generates itinerary
8. **Structured itinerary** displays with sections for flights, hotels, food, activities
9. **Source links** provided for each recommendation
10. **User can save** itinerary or start new search

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