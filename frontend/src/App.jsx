import { BrowserRouter as Router, Routes, Route, Link, useLocation, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, Calendar, Search, FileText, Brain, Map, Trophy, Users, Heart, BookOpen, Cloud, Camera } from 'lucide-react';
import { AuthWrapper } from './components/AuthWrapper';
import Landing from './components/Landing';
import Itinerary from './components/Itinerary';
import SmartPlanner from './components/SmartPlanner';
import SearchInterface from './components/SearchInterface';
import TravelDocuments from './components/TravelDocuments';
import FlightSearch from './components/FlightSearch';
import HotelSearch from './components/HotelSearch';
import DailyPlanner from './components/DailyPlanner';
import CartoonMapJourney from './components/CartoonMapJourney';
import AIChat from './components/AIChat';
import TravelDocsManager from './components/TravelDocsManager';
import Achievements from './components/Achievements';
import MoodTracker from './components/MoodTracker';
import Scrapbook from './components/Scrapbook';
import WeatherPlanning from './components/WeatherPlanning';
import GroupSync from './components/GroupSync';

// Navigation Component
function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/planner', label: 'Planner', icon: Brain },
    { path: '/journey', label: 'Journey', icon: Map },
    { path: '/achievements', label: 'Achievements', icon: Trophy },
    { path: '/scrapbook', label: 'Scrapbook', icon: Camera },
    { path: '/group', label: 'Group', icon: Users },
    { path: '/documents', label: 'Docs', icon: FileText }
  ];

  if (location.pathname === '/') return null;

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-white shadow-lg border-b sticky top-0 z-50"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            TravelAI
          </Link>
          
          <div className="flex space-x-1">
            {navItems.map(item => {
              const IconComponent = item.icon;
              const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <IconComponent className="w-4 h-4" />
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}

// Page wrapper components
function DailyPlannerPage() {
  const { tripId, date } = useParams();
  return (
    <div className="container mx-auto px-4 py-8">
      <DailyPlanner tripId={tripId} date={date} />
    </div>
  );
}

function JourneyPage() {
  const { tripId } = useParams();
  
  if (tripId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <CartoonMapJourney tripId={tripId} />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Your Travel Journey</h1>
        <p className="text-gray-600">Select a trip to view your progress map</p>
      </div>
      <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200 text-center">
        <Map className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p className="text-gray-500">No active journeys found. Create a trip first!</p>
        <Link 
          to="/planner" 
          className="inline-block mt-4 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Create Your First Trip
        </Link>
      </div>
    </div>
  );
}

function ScrapbookPage() {
  const { tripId } = useParams();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <Scrapbook tripId={tripId} />
    </div>
  );
}

function GroupPage() {
  const { tripId } = useParams();
  
  if (tripId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <GroupSync tripId={tripId} />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Group Travel</h1>
        <p className="text-gray-600">Travel together, sync activities, and share achievements</p>
      </div>
      <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200 text-center">
        <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p className="text-gray-500">Select a trip to create or join a group</p>
        <Link 
          to="/planner" 
          className="inline-block mt-4 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          View Your Trips
        </Link>
      </div>
    </div>
  );
}

function DocsPage() {
  const { tripId } = useParams();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <TravelDocsManager tripId={tripId} />
    </div>
  );
}

function WeatherPlanningPage() {
  const { location, date } = useParams();
  return (
    <div className="container mx-auto px-4 py-8">
      <WeatherPlanning location={decodeURIComponent(location)} date={date} />
    </div>
  );
}

function MoodTrackerPage() {
  const { slotId, tripId } = useParams();
  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <MoodTracker 
        slotId={slotId} 
        tripId={tripId} 
        onMoodTracked={(data) => {
          console.log('Mood tracked:', data);
          // Could redirect back or show success message
        }}
      />
    </div>
  );
}

function AchievementsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <Achievements />
    </div>
  );
}

function App() {
  return (
    <AuthWrapper>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <Routes>
            {/* Main Pages */}
            <Route path="/" element={<Landing />} />
            <Route path="/planner" element={<SmartPlanner />} />
            <Route path="/achievements" element={<AchievementsPage />} />
            
            {/* Feature Pages with Optional Trip ID */}
            <Route path="/journey" element={<JourneyPage />} />
            <Route path="/journey/:tripId" element={<JourneyPage />} />
            
            <Route path="/scrapbook" element={<ScrapbookPage />} />
            <Route path="/scrapbook/:tripId" element={<ScrapbookPage />} />
            
            <Route path="/group" element={<GroupPage />} />
            <Route path="/group/:tripId" element={<GroupPage />} />
            
            <Route path="/documents" element={<DocsPage />} />
            <Route path="/documents/:tripId" element={<DocsPage />} />
            
            {/* Specific Feature Pages */}
            <Route path="/planner/:tripId/:date" element={<DailyPlannerPage />} />
            <Route path="/weather/:location/:date" element={<WeatherPlanningPage />} />
            <Route path="/mood/:slotId/:tripId" element={<MoodTrackerPage />} />
            
            {/* Legacy routes */}
            <Route path="/search" element={<SearchInterface />} />
            <Route path="/itinerary" element={<Itinerary />} />
            <Route path="/flights" element={<FlightSearch />} />
            <Route path="/hotels" element={<HotelSearch />} />
          </Routes>
          
          {/* Global AI Chat - appears on all pages except landing */}
          {window.location.pathname !== '/' && <AIChat />}
        </div>
      </Router>
    </AuthWrapper>
  );
}

export default App;