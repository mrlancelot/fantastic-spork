import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Calendar, Users, MapPin, Star, Wifi, Car, Coffee, Heart } from 'lucide-react';
import { api } from '../utils/api';

const HotelSearch = () => {
  const [searchData, setSearchData] = useState({
    cityCode: '',
    checkInDate: '',
    checkOutDate: '',
    adults: 1,
    rooms: 1
  });

  const [hotels, setHotels] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sentiments, setSentiments] = useState({});

  const handleInputChange = (field, value) => {
    setSearchData(prev => ({ ...prev, [field]: value }));
  };

  const searchHotels = async () => {
    if (!searchData.cityCode || !searchData.checkInDate || !searchData.checkOutDate) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.hotels.search(
        searchData.cityCode,
        null,
        null,
        searchData.checkInDate,
        searchData.checkOutDate,
        searchData.adults,
        searchData.rooms
      );

      setHotels(result.hotels);

      // Get sentiment analysis for hotels
      if (result.hotels?.length > 0) {
        const hotelIds = result.hotels.slice(0, 5).map(hotel => hotel.id).filter(Boolean);
        if (hotelIds.length > 0) {
          try {
            const sentimentResult = await api.hotels.getSentiments(hotelIds);
            setSentiments(sentimentResult.sentiments || {});
          } catch (error) {
            console.warn('Failed to get hotel sentiments:', error);
          }
        }
      }
    } catch (error) {
      setError(`Hotel search failed: ${error.message}`);
      console.error('Hotel search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      case 'neutral': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const renderStars = (rating) => {
    if (!rating) return null;
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
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
          <Building2 className="text-purple-600 w-8 h-8" />
          <h2 className="text-2xl font-bold text-gray-800">Hotel Search</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {/* City/Destination */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <MapPin className="inline w-4 h-4 mr-1" />
              City Code
            </label>
            <input
              type="text"
              placeholder="e.g., PAR, NYC, LON"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              value={searchData.cityCode}
              onChange={(e) => handleInputChange('cityCode', e.target.value)}
            />
          </div>

          {/* Check-in Date */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Check-in
            </label>
            <input
              type="date"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              value={searchData.checkInDate}
              onChange={(e) => handleInputChange('checkInDate', e.target.value)}
            />
          </div>

          {/* Check-out Date */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Check-out
            </label>
            <input
              type="date"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              value={searchData.checkOutDate}
              onChange={(e) => handleInputChange('checkOutDate', e.target.value)}
            />
          </div>

          {/* Guests */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Users className="inline w-4 h-4 mr-1" />
              Guests
            </label>
            <input
              type="number"
              min="1"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              value={searchData.adults}
              onChange={(e) => handleInputChange('adults', parseInt(e.target.value))}
            />
          </div>

          {/* Rooms */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Rooms
            </label>
            <input
              type="number"
              min="1"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              value={searchData.rooms}
              onChange={(e) => handleInputChange('rooms', parseInt(e.target.value))}
            />
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
          onClick={searchHotels}
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching Hotels...' : 'Search Hotels'}
        </motion.button>
      </motion.div>

      {/* Hotel Results */}
      <AnimatePresence>
        {hotels && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <h3 className="text-xl font-bold text-gray-800">Hotel Options</h3>
            
            {hotels?.map((hotel, index) => {
              const hotelInfo = hotel;
              const offers = [];
              const sentiment = sentiments[hotel?.id];
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Building2 className="w-6 h-6 text-purple-600" />
                        <div>
                          <h4 className="font-semibold text-gray-800 text-lg">
                            {hotelInfo?.name}
                          </h4>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-600">
                              {hotelInfo?.address}
                            </span>
                          </div>
                          {hotelInfo?.distance && (
                            <span className="text-xs text-gray-500">
                              {hotelInfo.distance} from center
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Hotel Amenities */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {hotelInfo?.amenities?.slice(0, 4).map((amenity, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs"
                          >
                            {amenity.description}
                          </span>
                        )) || (
                          <>
                            <span className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                              <Wifi className="w-3 h-3" /> WiFi
                            </span>
                            <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                              <Car className="w-3 h-3" /> Parking
                            </span>
                            <span className="flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs">
                              <Coffee className="w-3 h-3" /> Breakfast
                            </span>
                          </>
                        )}
                      </div>

                      {/* Sentiment Analysis */}
                      {sentiment && (
                        <div className="mb-3">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(sentiment.overall_sentiment)}`}>
                            Guest Sentiment: {sentiment.overall_sentiment || 'Analyzing...'}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className="text-right ml-4">
                      <p className="text-lg font-semibold text-gray-700">
                        Rating: {hotelInfo?.rating}
                      </p>
                      <p className="text-sm text-gray-600">
                        Hotel ID: {hotelInfo?.id}
                      </p>
                    </div>
                  </div>


                  <div className="flex gap-3 mt-4">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="flex-1 bg-purple-600 text-white py-2 rounded-lg font-medium hover:bg-purple-700 transition-colors"
                    >
                      Book Now
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <Heart className="w-5 h-5 text-gray-600" />
                    </motion.button>
                  </div>
                </motion.div>
              );
            })}
            
            {(!hotels || hotels.length === 0) && (
              <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">No hotels found</h3>
                <p className="text-gray-500">Try adjusting your search criteria</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HotelSearch;