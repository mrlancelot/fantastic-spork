import { BrowserRouter as Router, Routes, Route, Link, useLocation, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, Calendar, Search, FileText, Brain, Map, Trophy, Users, Heart, BookOpen, Cloud, Camera, Bot } from 'lucide-react';
import { useQuery } from 'convex/react';
import { api } from '../convex/_generated/api';
import { AuthWrapper } from './components/AuthWrapper';
import { ConfettiProvider } from './contexts/ConfettiContext';
import ConfettiToggle from './components/ConfettiToggle';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './components/Landing';
import Itinerary from './components/Itinerary';
import SearchPage from './components/SearchPage';
import SmartPlanner from './components/SmartPlanner';
import DailyPlanner from './components/DailyPlanner';
import CartoonMapJourney from './components/CartoonMapJourney';
import AIChat from './components/AIChat';
import AgentChat from './components/AgentChat';
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
    { path: '/agent', label: 'AI Agent', icon: Bot },
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
  const currentUser = useQuery(api.users.getMyUser);
  const activeItinerary = useQuery(api.richItineraries.getActiveItinerary, 
    currentUser?._id ? { userId: currentUser._id } : "skip"
  );
  
  // If specific trip ID is provided, use it
  if (tripId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <CartoonMapJourney tripId={tripId} />
      </div>
    );
  }
  
  // If there's an active itinerary, show journey progress
  if (activeItinerary) {
    const { journeyData, destination, dailyPlans } = activeItinerary;
    const completedSlots = journeyData?.completed || 0;
    const totalSlots = journeyData?.totalActivities || 0;
    const progressPercentage = journeyData?.progressPercentage || 0;
    
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">
            Your Journey to {destination}
          </h1>
          <div className="max-w-md mx-auto">
            <div className="bg-white rounded-lg p-6 shadow-lg">
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{completedSlots} / {totalSlots} activities</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-600">
                  Level {journeyData?.currentLevel || 1} of {journeyData?.levels || 1}
                </p>
              </div>
              
              {/* Display unlocked badges */}
              {journeyData?.badges && (
                <div className="flex justify-center gap-4 mb-4">
                  {journeyData.badges.filter(b => b.unlocked).map(badge => (
                    <div key={badge.id} className="text-center">
                      <div className="text-3xl mb-1">{badge.icon}</div>
                      <p className="text-xs text-gray-600">{badge.name}</p>
                    </div>
                  ))}
                </div>
              )}
              
              <Link 
                to="/planner/smart" 
                className="inline-block w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-opacity text-center"
              >
                View Full Itinerary
              </Link>
            </div>
          </div>
        </div>
        
        {/* Visual journey map requires tripId - not showing without it */}
      </div>
    );
  }
  
  // No active journey
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Your Travel Journey</h1>
        <p className="text-gray-600">Track your progress through amazing destinations</p>
      </div>
      <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200 text-center">
        <Map className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p className="text-gray-500">No active journeys found. Create an itinerary to start your adventure!</p>
        <Link 
          to="/planner/smart" 
          className="inline-block mt-4 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Create Your Journey
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
      <ConfettiProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Navigation />
            <Routes>
            {/* Main Pages */}
            <Route path="/" element={<Landing />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/agent" element={<ProtectedRoute><AgentChat /></ProtectedRoute>} />
            <Route path="/planner" element={<ProtectedRoute><SmartPlanner /></ProtectedRoute>} />
            <Route path="/achievements" element={<ProtectedRoute><AchievementsPage /></ProtectedRoute>} />
            
            {/* Feature Pages with Optional Trip ID */}
            <Route path="/journey" element={<ProtectedRoute><JourneyPage /></ProtectedRoute>} />
            <Route path="/journey/:tripId" element={<ProtectedRoute><JourneyPage /></ProtectedRoute>} />
            
            <Route path="/scrapbook" element={<ProtectedRoute><ScrapbookPage /></ProtectedRoute>} />
            <Route path="/scrapbook/:tripId" element={<ProtectedRoute><ScrapbookPage /></ProtectedRoute>} />
            
            <Route path="/group" element={<ProtectedRoute><GroupPage /></ProtectedRoute>} />
            <Route path="/group/:tripId" element={<ProtectedRoute><GroupPage /></ProtectedRoute>} />
            
            <Route path="/documents" element={<ProtectedRoute><DocsPage /></ProtectedRoute>} />
            <Route path="/documents/:tripId" element={<ProtectedRoute><DocsPage /></ProtectedRoute>} />
            
            {/* Specific Feature Pages */}
            <Route path="/planner/:tripId/:date" element={<ProtectedRoute><DailyPlannerPage /></ProtectedRoute>} />
            <Route path="/weather/:location/:date" element={<ProtectedRoute><WeatherPlanningPage /></ProtectedRoute>} />
            <Route path="/mood/:slotId/:tripId" element={<ProtectedRoute><MoodTrackerPage /></ProtectedRoute>} />
            
            {/* Itinerary route - protected */}
            <Route path="/itinerary" element={<ProtectedRoute><Itinerary /></ProtectedRoute>} />
          </Routes>
          
          {/* Global AI Chat - appears on all pages except landing */}
          {window.location.pathname !== '/' && <AIChat />}
          
          <ConfettiToggle />
        </div>
      </Router>
    </ConfettiProvider>
  </AuthWrapper>
  );
}

export default App;