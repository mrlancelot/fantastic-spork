import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  MapPin, 
  Calendar, 
  Users, 
  Plane,
  Building,
  UtensilsCrossed,
  ActivitySquare,
  Clock,
  ExternalLink,
  Save,
  Loader2,
  ArrowLeft,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, CardHeader, CardTitle, CardContent, Badge } from './ui';
import { BookingButton } from './ui/BookingButton';
import { ContactInfo } from './ui/ContactInfo';
import { useCurrentUser } from '../hooks/useCurrentUser';

const Itinerary = () => {
  const navigate = useNavigate();
  const { userId, userName } = useCurrentUser();
  const [tripData, setTripData] = useState(null);
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [bookingValidation, setBookingValidation] = useState(null);

  useEffect(() => {
    // Get form data from localStorage
    const storedTripData = localStorage.getItem('tripData');
    if (!storedTripData) {
      // If no trip data, redirect back to landing
      navigate('/');
      return;
    }

    const parsedTripData = JSON.parse(storedTripData);
    setTripData(parsedTripData);

    // Check if there's a saved itinerary
    const savedItinerary = localStorage.getItem('savedItinerary');
    if (savedItinerary) {
      const itineraryData = JSON.parse(savedItinerary);
      setItinerary(itineraryData);
      setLoading(false);
      // Clean up
      localStorage.removeItem('savedItinerary');
    } else {
      // Generate new itinerary
      generateItinerary(parsedTripData);
    }
  }, [navigate]);

  const generateItinerary = async (data) => {
    try {
      setLoading(true);
      setError(null);

      // Use environment-appropriate API URL
      const apiUrl = import.meta.env.PROD 
        ? '' 
        : 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/api/planner/smart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination: data.destination,
          start_date: data.dates?.split(' to ')[0] || new Date().toISOString().split('T')[0],
          end_date: data.dates?.split(' to ')[1] || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          travelers: data.travelers || 1,
          interests: data.interests || [],
          budget: data.budget || 1000,
          pace: 'moderate'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setItinerary(result.itinerary);
      setBookingValidation(result.booking_validation);
    } catch (err) {
      console.error('Error generating itinerary:', err);
      setError('Failed to generate itinerary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveItinerary = async () => {
    if (!itinerary) return;

    try {
      setSaving(true);
      
      // Use environment-appropriate API URL
      const apiUrl = import.meta.env.PROD 
        ? '' 
        : 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/api/save-itinerary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          itinerary_data: {
            destination: tripData.destination,
            dates: tripData.dates,
            travelers: tripData.travelers,
            departureCities: tripData.departureCities,
            itinerary: itinerary,
            booking_validation: bookingValidation
          },
          trip_details: {
            destination: tripData.destination,
            dates: tripData.dates,
            travelers: tripData.travelers,
            departureCities: tripData.departureCities
          },
          user_id: userId
        }),
      });

      if (response.ok) {
        // Show success message or redirect
        alert('Itinerary saved successfully!');
      }
    } catch (err) {
      console.error('Error saving itinerary:', err);
      alert('Failed to save itinerary. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Generating Your Perfect Itinerary
          </h2>
          <p className="text-gray-600">
            Our AI is crafting personalized recommendations just for you...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
          <Button onClick={() => navigate('/')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Planning
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-start mb-8"
        >
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              {tripData?.destination}
            </h1>
            <div className="flex items-center gap-6 text-gray-600 mb-4">
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {tripData?.dates}
              </span>
              <span className="flex items-center">
                <Users className="w-4 h-4 mr-1" />
                {tripData?.travelers} travelers
              </span>
              <span className="flex items-center">
                <Plane className="w-4 h-4 mr-1" />
                From {tripData?.departureCities?.join(', ')}
              </span>
            </div>
            
            {/* Booking Validation Status */}
            {bookingValidation && (
              <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-600 font-medium">Booking Options Available:</span>
                <div className="flex items-center gap-1">
                  {bookingValidation.has_flight_bookings ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-orange-500" />
                  )}
                  <span className="text-xs text-gray-600">Flights</span>
                </div>
                <div className="flex items-center gap-1">
                  {bookingValidation.has_hotel_bookings ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-orange-500" />
                  )}
                  <span className="text-xs text-gray-600">Hotels</span>
                </div>
                <div className="flex items-center gap-1">
                  {bookingValidation.has_restaurant_bookings ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-orange-500" />
                  )}
                  <span className="text-xs text-gray-600">Restaurants</span>
                </div>
                <div className="flex items-center gap-1">
                  {bookingValidation.has_activity_bookings ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-orange-500" />
                  )}
                  <span className="text-xs text-gray-600">Activities</span>
                </div>
              </div>
            )}
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() => navigate('/')}
              variant="outline"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              New Search
            </Button>
            <Button
              onClick={handleSaveItinerary}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Save Itinerary
            </Button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Main Content */}
          <div className="space-y-6">
            {/* Trip Summary */}
            {itinerary?.summary && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                      Trip Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">{itinerary.summary}</p>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Flights */}
            {itinerary?.flights && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Plane className="w-5 h-5 mr-2 text-blue-600" />
                      Flights
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {itinerary.flights.map((flight, index) => (
                      <div key={index} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h4 className="font-semibold text-lg">{flight.airline}</h4>
                            <p className="text-sm text-gray-600">From {flight.from}</p>
                          </div>
                          {flight.price_range && (
                            <Badge variant="outline" className="text-lg px-3 py-1">
                              {flight.price_range}
                            </Badge>
                          )}
                        </div>
                        
                        {/* Booking Options */}
                        {flight.booking_options && flight.booking_options.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-3">Booking Options:</h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              {flight.booking_options.map((option, optionIndex) => (
                                <BookingButton key={optionIndex} option={option} />
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Fallback for old format */}
                        {flight.source_url && !flight.booking_options && (
                          <a 
                            href={flight.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                          >
                            View Details <ExternalLink className="w-3 h-3 ml-1" />
                          </a>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Accommodations */}
            {itinerary?.accommodations && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Building className="w-5 h-5 mr-2 text-blue-600" />
                      Accommodations
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {itinerary.accommodations.map((hotel, index) => (
                      <div key={index} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <h4 className="font-semibold text-lg">{hotel.name}</h4>
                            <p className="text-sm text-gray-600 mb-2">{hotel.neighborhood}</p>
                            {hotel.bachelor_friendly && (
                              <Badge className="bg-green-100 text-green-800 border-green-200" variant="outline">
                                Group Friendly
                              </Badge>
                            )}
                          </div>
                          {hotel.price_per_night && (
                            <Badge variant="outline" className="text-lg px-3 py-1">
                              {hotel.price_per_night}/night
                            </Badge>
                          )}
                        </div>
                        
                        {/* Booking Options */}
                        {hotel.booking_options && hotel.booking_options.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-3">Booking Options:</h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              {hotel.booking_options.map((option, optionIndex) => (
                                <BookingButton key={optionIndex} option={option} />
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Fallback for old format */}
                        {hotel.source_url && !hotel.booking_options && (
                          <a 
                            href={hotel.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                          >
                            View Details <ExternalLink className="w-3 h-3 ml-1" />
                          </a>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Food Recommendations */}
            {itinerary?.food && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <UtensilsCrossed className="w-5 h-5 mr-2 text-blue-600" />
                      Food & Dining
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {itinerary.food.map((restaurant, index) => (
                      <div key={index} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <h4 className="font-semibold text-lg">{restaurant.name}</h4>
                            <p className="text-sm text-gray-600 mb-2">{restaurant.cuisine}</p>
                            {restaurant.good_for_groups && (
                              <Badge className="bg-green-100 text-green-800 border-green-200" variant="outline">
                                Great for Groups
                              </Badge>
                            )}
                          </div>
                          {restaurant.price_range && (
                            <Badge variant="outline" className="text-lg px-3 py-1">
                              {restaurant.price_range}
                            </Badge>
                          )}
                        </div>
                        
                        {/* Booking Options */}
                        {restaurant.booking_options && restaurant.booking_options.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-3">Reservation Options:</h5>
                            <div className="grid grid-cols-1 gap-3">
                              {restaurant.booking_options.map((option, optionIndex) => (
                                <BookingButton key={optionIndex} option={option} className="max-w-sm" />
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Fallback for old format */}
                        {restaurant.source_url && !restaurant.booking_options && (
                          <a 
                            href={restaurant.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                          >
                            View Details <ExternalLink className="w-3 h-3 ml-1" />
                          </a>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Activities */}
            {itinerary?.activities && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <ActivitySquare className="w-5 h-5 mr-2 text-blue-600" />
                      Activities
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {itinerary.activities.map((activity, index) => (
                      <div key={index} className="p-4 border border-gray-200 rounded-lg">
                        <div className="mb-4">
                          <h4 className="font-semibold text-lg">{activity.name}</h4>
                          <p className="text-sm text-gray-600 capitalize mb-2">{activity.type}</p>
                          {activity.bachelor_appropriate && (
                            <Badge className="bg-green-100 text-green-800 border-green-200" variant="outline">
                              Group Appropriate
                            </Badge>
                          )}
                        </div>
                        
                        {/* Booking Options */}
                        {activity.booking_options && activity.booking_options.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-3">Booking Options:</h5>
                            <div className="grid grid-cols-1 gap-3">
                              {activity.booking_options.map((option, optionIndex) => (
                                <BookingButton key={optionIndex} option={option} className="max-w-sm" />
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Fallback for old format */}
                        {activity.source_url && !activity.booking_options && (
                          <a 
                            href={activity.source_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                          >
                            View Details <ExternalLink className="w-3 h-3 ml-1" />
                          </a>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </div>

        {/* Booking Summary */}
        {itinerary?.booking_summary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mt-8"
          >
            <Card className="bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center text-blue-800">
                  <Save className="w-5 h-5 mr-2" />
                  Booking Summary & Tips
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {itinerary.booking_summary.total_estimated_cost && (
                  <div className="p-4 bg-white rounded-lg border">
                    <h4 className="font-semibold text-lg text-gray-900 mb-2">
                      Total Estimated Cost
                    </h4>
                    <p className="text-2xl font-bold text-blue-600">
                      {itinerary.booking_summary.total_estimated_cost}
                    </p>
                  </div>
                )}
                
                {itinerary.booking_summary.best_booking_strategy && (
                  <div className="p-4 bg-white rounded-lg border">
                    <h4 className="font-semibold text-lg text-gray-900 mb-2">
                      Best Booking Strategy
                    </h4>
                    <p className="text-gray-700">
                      {itinerary.booking_summary.best_booking_strategy}
                    </p>
                  </div>
                )}
                
                {itinerary.booking_summary.group_booking_tips && (
                  <div className="p-4 bg-white rounded-lg border">
                    <h4 className="font-semibold text-lg text-gray-900 mb-3">
                      Group Booking Tips
                    </h4>
                    <ul className="space-y-2">
                      {itinerary.booking_summary.group_booking_tips.map((tip, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                          <span className="text-gray-700">{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Daily Schedule */}
        {itinerary?.schedule && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mt-8"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-blue-600" />
                  Daily Schedule
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {Object.entries(itinerary.schedule).map(([day, activities]) => (
                    <div key={day} className="space-y-3">
                      <h3 className="font-semibold text-lg capitalize text-gray-900">
                        {day.replace(/(\d+)/, 'Day $1')}
                      </h3>
                      <div className="space-y-2">
                        {activities.map((activity, index) => (
                          <div key={index} className="p-3 bg-blue-50 rounded-lg">
                            <p className="text-sm text-gray-700">{activity}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Sources */}
        {itinerary?.sources && itinerary.sources.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="mt-8"
          >
            <Card>
              <CardHeader>
                <CardTitle>Sources & References</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {itinerary.sources.map((source, index) => (
                    <a
                      key={index}
                      href={source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center text-sm text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      <ExternalLink className="w-3 h-3 mr-2" />
                      {source}
                    </a>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Itinerary;