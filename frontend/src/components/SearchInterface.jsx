import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Plane, Building2, MapPin, Calendar, Users, Search, Filter, Star } from 'lucide-react';
import { api } from '../utils/api';
import ConfettiEffect from './ui/ConfettiEffect';

export default function SearchInterface() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('flights');
  const [searchData, setSearchData] = useState({
    flights: {
      origin: '',
      destination: '',
      departureDate: '',
      returnDate: '',
      adults: 1,
      seatClass: 'economy'
    },
    hotels: {
      cityCode: '',
      checkInDate: '',
      checkOutDate: '',
      adults: 1,
      rooms: 1
    },
    activities: {
      location: '',
      latitude: null,
      longitude: null,
      radius: 5,
      adults: 1
    }
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSuccess, setShowSuccess] = useState(false);

  const tabs = [
    { id: 'flights', name: 'Flights', icon: Plane, color: 'from-blue-500 to-blue-600' },
    { id: 'hotels', name: 'Hotels', icon: Building2, color: 'from-green-500 to-green-600' },
    { id: 'activities', name: 'Activities', icon: MapPin, color: 'from-purple-500 to-purple-600' }
  ];

  const handleInputChange = (tab, field, value) => {
    setSearchData(prev => ({
      ...prev,
      [tab]: {
        ...prev[tab],
        [field]: value
      }
    }));
  };

  const handleSearch = async () => {
    if (loading) return;
    
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let response;
      const data = searchData[activeTab];

      switch (activeTab) {
        case 'flights':
          if (!data.origin || !data.destination || !data.departureDate) {
            throw new Error('Please fill in origin, destination, and departure date');
          }
          response = await api.searchFlights({
            origin: data.origin,
            destination: data.destination,
            departure_date: data.departureDate,
            return_date: data.returnDate,
            adults: data.adults,
            seat_class: data.seatClass
          });
          break;

        case 'hotels':
          if (!data.cityCode || !data.checkInDate || !data.checkOutDate) {
            throw new Error('Please fill in destination, check-in and check-out dates');
          }
          response = await api.searchHotels({
            city_code: data.cityCode,
            check_in_date: data.checkInDate,
            check_out_date: data.checkOutDate,
            adults: data.adults,
            rooms: data.rooms
          });
          break;

        case 'activities':
          if (!data.location) {
            throw new Error('Please enter a location');
          }
          // For demo, use approximate coordinates
          response = await api.searchActivities({
            latitude: data.latitude || 40.7128,
            longitude: data.longitude || -74.0060,
            radius: data.radius,
            adults: data.adults
          });
          break;
      }

      setResults(response);
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 2000);

    } catch (err) {
      setError(err.message);
      console.error(`${activeTab} search error:`, err);
    } finally {
      setLoading(false);
    }
  };

  const renderSearchForm = () => {
    const data = searchData[activeTab];
    
    switch (activeTab) {
      case 'flights':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
                <input
                  type="text"
                  placeholder="e.g. NYC, JFK, New York"
                  value={data.origin}
                  onChange={(e) => handleInputChange('flights', 'origin', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
                <input
                  type="text"
                  placeholder="e.g. LAX, Los Angeles"
                  value={data.destination}
                  onChange={(e) => handleInputChange('flights', 'destination', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Departure</label>
                <input
                  type="date"
                  value={data.departureDate}
                  onChange={(e) => handleInputChange('flights', 'departureDate', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Return (Optional)</label>
                <input
                  type="date"
                  value={data.returnDate}
                  onChange={(e) => handleInputChange('flights', 'returnDate', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Travelers</label>
                <select
                  value={data.adults}
                  onChange={(e) => handleInputChange('flights', 'adults', parseInt(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {[1,2,3,4,5,6,7,8].map(num => (
                    <option key={num} value={num}>{num} {num === 1 ? 'passenger' : 'passengers'}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
                <select
                  value={data.seatClass}
                  onChange={(e) => handleInputChange('flights', 'seatClass', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="economy">Economy</option>
                  <option value="premium_economy">Premium Economy</option>
                  <option value="business">Business</option>
                  <option value="first">First Class</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 'hotels':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Destination</label>
              <input
                type="text"
                placeholder="e.g. NYC, PAR, LON"
                value={data.cityCode}
                onChange={(e) => handleInputChange('hotels', 'cityCode', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Check-in</label>
                <input
                  type="date"
                  value={data.checkInDate}
                  onChange={(e) => handleInputChange('hotels', 'checkInDate', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Check-out</label>
                <input
                  type="date"
                  value={data.checkOutDate}
                  onChange={(e) => handleInputChange('hotels', 'checkOutDate', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Guests</label>
                <select
                  value={data.adults}
                  onChange={(e) => handleInputChange('hotels', 'adults', parseInt(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  {[1,2,3,4,5,6,7,8].map(num => (
                    <option key={num} value={num}>{num} {num === 1 ? 'guest' : 'guests'}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Rooms</label>
                <select
                  value={data.rooms}
                  onChange={(e) => handleInputChange('hotels', 'rooms', parseInt(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  {[1,2,3,4,5].map(num => (
                    <option key={num} value={num}>{num} {num === 1 ? 'room' : 'rooms'}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        );

      case 'activities':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <input
                type="text"
                placeholder="e.g. Paris, New York, Tokyo"
                value={data.location}
                onChange={(e) => handleInputChange('activities', 'location', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Search Radius (km)</label>
                <select
                  value={data.radius}
                  onChange={(e) => handleInputChange('activities', 'radius', parseInt(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value={1}>1 km</option>
                  <option value={5}>5 km</option>
                  <option value={10}>10 km</option>
                  <option value={25}>25 km</option>
                  <option value={50}>50 km</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Travelers</label>
                <select
                  value={data.adults}
                  onChange={(e) => handleInputChange('activities', 'adults', parseInt(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  {[1,2,3,4,5,6,7,8].map(num => (
                    <option key={num} value={num}>{num} {num === 1 ? 'traveler' : 'travelers'}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const renderResults = () => {
    if (!results) return null;

    const activeTabData = tabs.find(tab => tab.id === activeTab);
    const IconComponent = activeTabData.icon;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-8 bg-white rounded-xl shadow-lg overflow-hidden"
      >
        <div className={`bg-gradient-to-r ${activeTabData.color} text-white p-4`}>
          <div className="flex items-center gap-2">
            <IconComponent className="w-5 h-5" />
            <h3 className="text-lg font-semibold">Search Results</h3>
          </div>
        </div>
        
        <div className="p-4">
          {results && results.status === 'success' ? (
            <div className="space-y-3">
              {activeTab === 'flights' && results.flights && results.flights.length > 0 ? (
                results.flights.map((flight, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {flight.airline} Flight {flight.flight_number}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">
                          {flight.departure_time} → {flight.arrival_time}
                        </p>
                        <p className="text-xs text-gray-500">
                          Duration: {flight.duration} • {flight.stops === 0 ? 'Nonstop' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-900">
                          {flight.price}
                        </p>
                        <button 
                          onClick={() => {
                            navigate('/flights', { 
                              state: { 
                                flight: flight,
                                searchParams: searchData.flights 
                              } 
                            });
                          }}
                          className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                        >
                          Select
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : activeTab === 'hotels' && results.hotels && results.hotels.length > 0 ? (
                results.hotels.map((hotel, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {hotel.name}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">
                          📍 {hotel.address}
                        </p>
                        {(hotel.distance && hotel.distance !== 'N/A' || hotel.rating && hotel.rating !== 'N/A') && (
                          <p className="text-xs text-gray-500">
                            {hotel.distance && hotel.distance !== 'N/A' && `Distance: ${hotel.distance}`}
                            {hotel.distance && hotel.distance !== 'N/A' && hotel.rating && hotel.rating !== 'N/A' && ' • '}
                            {hotel.rating && hotel.rating !== 'N/A' && `Rating: ${hotel.rating}`}
                          </p>
                        )}
                        {hotel.id && (
                          <p className="text-xs text-gray-400 mt-1">
                            Hotel ID: {hotel.id}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <button 
                          onClick={() => {
                            // Navigate to hotel search page with this hotel selected
                            navigate('/hotels', { 
                              state: { 
                                hotel: hotel,
                                searchParams: searchData.hotels 
                              } 
                            });
                          }}
                          className="mt-2 bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700 transition-colors"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : activeTab === 'activities' && results.activities && results.activities.length > 0 ? (
                results.activities.map((activity, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {activity.name}
                        </h4>
                        {activity.description && (
                          <p className="text-sm text-gray-600 mb-2">
                            {activity.description}
                          </p>
                        )}
                        {activity.rating && (
                          <p className="text-xs text-gray-500">
                            Rating: {activity.rating}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        {activity.price && (
                          <p className="text-lg font-bold text-gray-900">
                            {activity.currency} {activity.price}
                          </p>
                        )}
                        <button className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors">
                          Book Now
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No results found. Please try different search criteria.
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No results found. Please try different search criteria.
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <ConfettiEffect show={showSuccess} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Travel Search Hub 🔍
            </h1>
            <p className="text-gray-600 text-lg">
              Find the best flights, hotels, and activities for your trip
            </p>
          </motion.div>

          {/* Tab Navigation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center mb-8"
          >
            <div className="bg-white rounded-xl shadow-lg p-2 flex gap-2">
              {tabs.map(tab => {
                const IconComponent = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                      activeTab === tab.id
                        ? `bg-gradient-to-r ${tab.color} text-white shadow-md`
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                    {tab.name}
                  </button>
                );
              })}
            </div>
          </motion.div>

          {/* Search Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl p-8 mb-8"
          >
            {renderSearchForm()}

            {error && (
              <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {error}
              </div>
            )}

            <motion.button
              onClick={handleSearch}
              disabled={loading}
              className={`w-full mt-6 py-4 rounded-lg font-semibold text-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                activeTab === 'flights' ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700' :
                activeTab === 'hotels' ? 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700' :
                'bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:from-purple-600 hover:to-purple-700'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-2"></div>
                  Searching...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <Search className="w-5 h-5 mr-2" />
                  Search {tabs.find(tab => tab.id === activeTab)?.name}
                </div>
              )}
            </motion.button>
          </motion.div>

          {/* Results */}
          {renderResults()}
        </div>
      </div>
    </div>
  );
}