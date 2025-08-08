import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plane, Calendar, Users, MapPin, DollarSign, Clock, Building } from 'lucide-react';
import { api } from '../utils/api';

const FlightSearch = () => {
  const [searchData, setSearchData] = useState({
    origin: '',
    destination: '',
    departureDate: '',
    returnDate: '',
    adults: 1,
    seatClass: 'economy'
  });

  const [flights, setFlights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tripType, setTripType] = useState('round-trip');

  const handleInputChange = (field, value) => {
    setSearchData(prev => ({ ...prev, [field]: value }));
  };

  const searchFlights = async () => {
    if (!searchData.origin || !searchData.destination || !searchData.departureDate) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.flights.search(
        searchData.origin,
        searchData.destination,
        searchData.departureDate,
        tripType === 'round-trip' ? searchData.returnDate : null,
        searchData.adults,
        searchData.seatClass
      );

      setFlights(result.flights);
    } catch (error) {
      setError(`Flight search failed: ${error.message}`);
      console.error('Flight search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Search Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-xl p-8"
      >
        <div className="flex items-center gap-3 mb-6">
          <Plane className="text-blue-600 w-8 h-8" />
          <h2 className="text-2xl font-bold text-gray-800">Flight Search</h2>
        </div>

        {/* Trip Type */}
        <div className="mb-6">
          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                value="round-trip"
                checked={tripType === 'round-trip'}
                onChange={(e) => setTripType(e.target.value)}
                className="text-blue-600"
              />
              <span>Round Trip</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                value="one-way"
                checked={tripType === 'one-way'}
                onChange={(e) => setTripType(e.target.value)}
                className="text-blue-600"
              />
              <span>One Way</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Origin */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <MapPin className="inline w-4 h-4 mr-1" />
              From
            </label>
            <input
              type="text"
              placeholder="Origin (e.g., NYC, LAX)"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchData.origin}
              onChange={(e) => handleInputChange('origin', e.target.value)}
            />
          </div>

          {/* Destination */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <MapPin className="inline w-4 h-4 mr-1" />
              To
            </label>
            <input
              type="text"
              placeholder="Destination (e.g., PAR, LON)"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchData.destination}
              onChange={(e) => handleInputChange('destination', e.target.value)}
            />
          </div>

          {/* Departure Date */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Departure
            </label>
            <input
              type="date"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchData.departureDate}
              onChange={(e) => handleInputChange('departureDate', e.target.value)}
            />
          </div>

          {/* Return Date */}
          {tripType === 'round-trip' && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <Calendar className="inline w-4 h-4 mr-1" />
                Return
              </label>
              <input
                type="date"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchData.returnDate}
                onChange={(e) => handleInputChange('returnDate', e.target.value)}
              />
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Passengers */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Users className="inline w-4 h-4 mr-1" />
              Passengers
            </label>
            <input
              type="number"
              min="1"
              max="9"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchData.adults}
              onChange={(e) => handleInputChange('adults', parseInt(e.target.value))}
            />
          </div>

          {/* Seat Class */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Class
            </label>
            <select
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchData.seatClass}
              onChange={(e) => handleInputChange('seatClass', e.target.value)}
            >
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First Class</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={searchFlights}
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching Flights...' : 'Search Flights'}
        </motion.button>
      </motion.div>

      {/* Flight Results */}
      <AnimatePresence>
        {flights && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <h3 className="text-xl font-bold text-gray-800">Flight Options</h3>
            
            {flights?.map((flight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Plane className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800">
                        {flight.airline} - Flight {flight.flight_number}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {flight.stops || 0} stop(s)
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">
                      {flight.price}
                    </p>
                    <p className="text-sm text-gray-600">per person</p>
                  </div>
                </div>

                {/* Flight Details */}
                <div className="mb-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-4">
                      <Clock className="w-4 h-4 text-gray-600" />
                      <div>
                        <p className="font-medium">
                          {flight.departure_time}
                        </p>
                        <p className="text-sm text-gray-600">
                          {searchData.origin.toUpperCase()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex-1 text-center">
                      <p className="text-sm text-gray-600">
                        Duration: {flight.duration}
                      </p>
                      <div className="w-full h-1 bg-gray-300 rounded-full mt-1"></div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-medium">
                          {flight.arrival_time}
                        </p>
                        <p className="text-sm text-gray-600">
                          {searchData.destination.toUpperCase()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Select Flight
                </motion.button>
              </motion.div>
            ))}
            
            {(!flights || flights.length === 0) && (
              <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                <Plane className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">No flights found</h3>
                <p className="text-gray-500">Try adjusting your search criteria</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FlightSearch;