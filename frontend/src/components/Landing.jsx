import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  MapPin, 
  Calendar, 
  Users, 
  Plane,
  ArrowRight,
  UserCircle,
  LogOut,
  Sparkles,
  Building2,
  Map,
  MessageCircle
} from 'lucide-react';
import { Button, Card, CardContent } from './ui';
import { useCurrentUser } from '../hooks/useCurrentUser';
import { TripList } from './TripList';
import { SignInButton, SignOutButton, SignUpButton } from '@clerk/clerk-react';

const Landing = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isSignedIn, userName, user } = useCurrentUser();
  const [showTripForm, setShowTripForm] = useState(false);
  const [editingTripId, setEditingTripId] = useState(null);
  const [formData, setFormData] = useState({
    destination: 'Buenos Aires and Patagonia',
    dates: 'November 2024',
    travelers: 6,
    departureCities: ['San Francisco', 'NYC']
  });

  const departureCityOptions = [
    'San Francisco',
    'NYC', 
    'LA',
    'Shanghai'
  ];

  // Handle editing trip from navigation state
  useEffect(() => {
    if (location.state?.editingTrip) {
      const trip = location.state.editingTrip;
      setEditingTripId(trip._id);
      setFormData({
        destination: trip.destination,
        dates: `${trip.startDate} to ${trip.endDate}`,
        travelers: trip.travelers,
        departureCities: trip.departureCities || []
      });
      setShowTripForm(true);
      
      // Clear the state to prevent re-loading on refresh
      navigate(location.pathname, { replace: true });
    }
  }, [location.state, navigate, location.pathname]);

  const handleDepartureCityChange = (city) => {
    setFormData(prev => ({
      ...prev,
      departureCities: prev.departureCities.includes(city)
        ? prev.departureCities.filter(c => c !== city)
        : [...prev.departureCities, city]
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Store form data in localStorage
    localStorage.setItem('tripData', JSON.stringify(formData));
    
    // Navigate to smart planner with trip data
    navigate('/planner', { state: { tripData: formData } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Auth Header */}
      <div className="absolute top-4 right-4 z-10">
        {isSignedIn ? (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <UserCircle className="w-5 h-5" />
              <span>Welcome, {userName}!</span>
            </div>
            <SignOutButton>
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                <LogOut className="w-4 h-4" />
                Sign Out
              </Button>
            </SignOutButton>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <SignInButton>
              <Button variant="outline" size="sm">Sign In</Button>
            </SignInButton>
            <SignUpButton>
              <Button size="sm">Sign Up</Button>
            </SignUpButton>
          </div>
        )}
      </div>

      {/* Hero Section */}
      <div className="pt-20 pb-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                TravelAI MVP
              </span>
            </h1>
            <p className="text-2xl md:text-3xl text-gray-700 mb-4">
              Smart Travel Planning Powered by AI
            </p>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
              Experience the future of travel planning with our integrated AI-powered platform featuring smart daily planners, real-time flight search, hotel sentiment analysis, and intelligent chat assistance.
            </p>
            
            {/* Quick Action Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/planner')}
                className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg"
              >
                <Sparkles className="w-5 h-5" />
                Smart Planner
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/search')}
                className="flex items-center gap-2 bg-white text-blue-600 px-6 py-3 rounded-xl font-semibold shadow-lg border-2 border-blue-200"
              >
                <Plane className="w-5 h-5" />
                Search Travel
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/documents')}
                className="flex items-center gap-2 bg-white text-purple-600 px-6 py-3 rounded-xl font-semibold shadow-lg border-2 border-purple-200"
              >
                <Building2 className="w-5 h-5" />
                Travel Docs
              </motion.button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Showcase */}
      {!isSignedIn && (
        <div className="pb-16 px-4">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Powerful Travel Planning Features</h2>
              <p className="text-lg text-gray-600">Everything you need for the perfect trip, powered by AI and real-time data</p>
            </motion.div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Smart Daily Planner */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl p-6 shadow-xl border border-purple-100 hover:shadow-2xl transition-all duration-300"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Smart Daily Planner</h3>
                <p className="text-gray-600 mb-4">AI-powered 4-slot daily planning with drag-drop, weather integration, and celebration animations</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Morning, Midday, Evening, Night slots</li>
                  <li>• Weather-aware planning</li>
                  <li>• Drag & drop reordering</li>
                  <li>• Confetti celebrations</li>
                </ul>
              </motion.div>

              {/* Flight Search */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-2xl p-6 shadow-xl border border-blue-100 hover:shadow-2xl transition-all duration-300"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4">
                  <Plane className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Flight Search</h3>
                <p className="text-gray-600 mb-4">Real-time flight data from Amadeus with smart routing and price analysis</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Real-time pricing</li>
                  <li>• Multi-airport search</li>
                  <li>• Delay predictions</li>
                  <li>• Cheapest date finder</li>
                </ul>
              </motion.div>

              {/* Hotel Search */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white rounded-2xl p-6 shadow-xl border border-pink-100 hover:shadow-2xl transition-all duration-300"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-pink-600 rounded-xl flex items-center justify-center mb-4">
                  <Building2 className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Hotel Intelligence</h3>
                <p className="text-gray-600 mb-4">Advanced hotel search with AI-powered sentiment analysis from guest reviews</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Sentiment analysis</li>
                  <li>• Price comparison</li>
                  <li>• Guest review insights</li>
                  <li>• Group booking options</li>
                </ul>
              </motion.div>

              {/* AI Chat */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-white rounded-2xl p-6 shadow-xl border border-green-100 hover:shadow-2xl transition-all duration-300"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-4">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">AI Travel Assistant</h3>
                <p className="text-gray-600 mb-4">Intelligent chat interface powered by advanced AI workflows for instant travel help</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Natural language queries</li>
                  <li>• Real-time recommendations</li>
                  <li>• Context-aware responses</li>
                  <li>• Travel expertise on demand</li>
                </ul>
              </motion.div>
            </div>
            
            {/* Map Journey Preview */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="mt-12 bg-white rounded-2xl p-8 shadow-xl"
            >
              <div className="text-center mb-6">
                <Map className="w-12 h-12 mx-auto text-blue-600 mb-4" />
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Cartoon Map Journey</h3>
                <p className="text-gray-600">Visual progress tracking with Angry Birds style progression through your travel adventure</p>
              </div>
              <div className="bg-gradient-to-r from-blue-100 via-purple-100 to-pink-100 rounded-xl p-8 text-center">
                <div className="flex justify-center items-center gap-4 text-4xl mb-4">
                  <span>🏠</span>
                  <span className="text-blue-500">→</span>
                  <span>✈️</span>
                  <span className="text-blue-500">→</span>
                  <span>🏔️</span>
                  <span className="text-blue-500">→</span>
                  <span>🌊</span>
                  <span className="text-blue-500">→</span>
                  <span>🎯</span>
                </div>
                <p className="text-gray-600">Track your journey progress with delightful animations and celebrations</p>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* Trip List for Authenticated Users */}
      {isSignedIn && !showTripForm && (
        <div className="pb-16 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-800">My Trips</h2>
              <Button 
                onClick={() => setShowTripForm(true)}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold"
              >
                <Sparkles className="w-5 h-5 mr-2" />
                Plan New Trip
              </Button>
            </div>
            <TripList />
          </div>
        </div>
      )}

      {/* Plan Trip Button or Form Section */}
      {!isSignedIn && !showTripForm && (
        <div className="pb-20 px-4">
          <div className="max-w-2xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Ready to Start Your Adventure?
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Let our AI create the perfect itinerary for your group trip
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowTripForm(true)}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-xl font-semibold shadow-lg text-lg"
              >
                <Sparkles className="w-6 h-6" />
                Plan Your Trip
                <ArrowRight className="w-6 h-6" />
              </motion.button>
            </motion.div>
          </div>
        </div>
      )}

      {/* Form Section */}
      {showTripForm && (
        <div className="pb-20 px-4">
          <div className="max-w-2xl mx-auto">
            {showTripForm && (
              <div className="mb-6 text-center">
                <Button 
                  variant="outline"
                  onClick={() => {
                    setShowTripForm(false);
                    setEditingTripId(null);
                    setFormData({
                      destination: 'Buenos Aires and Patagonia',
                      dates: 'November 2024',
                      travelers: 6,
                      departureCities: ['San Francisco', 'NYC']
                    });
                  }}
                  className="mb-4"
                >
                  ← Back {isSignedIn ? 'to My Trips' : ''}
                </Button>
              </div>
            )}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <Card className="bg-white shadow-2xl border-0">
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                  {editingTripId ? 'Edit Your Trip' : 'Plan Your Perfect Group Adventure'}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-8">
                  {/* Destination */}
                  <div>
                    <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                      <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                      Destination
                    </label>
                    <input
                      type="text"
                      value={formData.destination}
                      onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                      className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 transition-colors"
                      placeholder="Where would you like to go?"
                    />
                  </div>

                  {/* Travel Dates */}
                  <div>
                    <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                      <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                      Travel Dates
                    </label>
                    <input
                      type="text"
                      value={formData.dates}
                      onChange={(e) => setFormData(prev => ({ ...prev, dates: e.target.value }))}
                      className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 transition-colors"
                      placeholder="When are you traveling?"
                    />
                  </div>

                  {/* Number of Travelers */}
                  <div>
                    <label className="flex items-center text-lg font-semibold text-gray-900 mb-3">
                      <Users className="w-5 h-5 mr-2 text-blue-600" />
                      Number of Travelers
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="20"
                      value={formData.travelers}
                      onChange={(e) => setFormData(prev => ({ ...prev, travelers: parseInt(e.target.value) }))}
                      className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 transition-colors"
                    />
                  </div>

                  {/* Departure Cities */}
                  <div>
                    <label className="flex items-center text-lg font-semibold text-gray-900 mb-4">
                      <Plane className="w-5 h-5 mr-2 text-blue-600" />
                      Departure Cities
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      {departureCityOptions.map((city) => (
                        <label
                          key={city}
                          className="flex items-center space-x-3 p-4 border-2 border-gray-200 rounded-xl cursor-pointer transition-all hover:border-blue-300 hover:bg-blue-50"
                          style={{
                            borderColor: formData.departureCities.includes(city) ? '#3B82F6' : '#E5E7EB',
                            backgroundColor: formData.departureCities.includes(city) ? '#EFF6FF' : 'white'
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={formData.departureCities.includes(city)}
                            onChange={() => handleDepartureCityChange(city)}
                            className="w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span className="text-lg font-medium text-gray-900">
                            {city}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="flex gap-4">
                    {editingTripId && (
                      <Button
                        type="button"
                        size="lg"
                        variant="outline"
                        onClick={() => {
                          setEditingTripId(null);
                          setShowTripForm(false);
                          setFormData({
                            destination: 'Buenos Aires and Patagonia',
                            dates: 'November 2024',
                            travelers: 6,
                            departureCities: ['San Francisco', 'NYC']
                          });
                        }}
                        className="flex-1 py-4 px-8 rounded-xl"
                      >
                        Cancel
                      </Button>
                    )}
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="flex-1"
                    >
                      <Button
                        type="submit"
                        size="lg"
                        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-4 px-8 rounded-xl shadow-lg transition-all duration-200"
                      >
                        {editingTripId ? 'Update Trip' : 'Generate My Itinerary'}
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </Button>
                    </motion.div>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
      )}
    </div>
  );
};

export default Landing;