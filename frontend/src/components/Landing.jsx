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
  LogOut
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
    
    // Navigate to itinerary page
    navigate('/itinerary');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200">
      {/* Auth Header */}
      <div className="absolute top-4 right-4">
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
              <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                Waypoint
              </span>
            </h1>
            <p className="text-2xl md:text-3xl text-gray-700 mb-4">
              AI Travel Planner for Locals
            </p>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Create perfect itineraries with local insights and real-time recommendations
            </p>
          </motion.div>
        </div>
      </div>

      {/* Trip List for Authenticated Users */}
      {isSignedIn && !showTripForm && (
        <div className="pb-16 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <div />
              <Button 
                onClick={() => setShowTripForm(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Plan New Trip
              </Button>
            </div>
            <TripList />
          </div>
        </div>
      )}

      {/* Form Section */}
      {(!isSignedIn || showTripForm) && (
        <div className="pb-20 px-4">
          <div className="max-w-2xl mx-auto">
            {showTripForm && (
              <div className="mb-6 text-center">
                <Button 
                  variant="outline"
                  onClick={() => setShowTripForm(false)}
                  className="mb-4"
                >
                  ← Back to My Trips
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