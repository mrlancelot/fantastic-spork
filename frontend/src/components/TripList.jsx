import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation } from "convex/react";
import { api } from "../../convex/_generated/api";
import { Card, CardHeader, CardTitle, CardContent, Badge, Button } from './ui';
import { MapPin, Calendar, Users, ExternalLink, Edit, Trash2, Eye, MoreVertical } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useCurrentUser } from '../hooks/useCurrentUser';

export function TripList() {
  const navigate = useNavigate();
  const { userId } = useCurrentUser();
  const trips = useQuery(api.trips.getUserTrips);
  const deleteTrip = useMutation(api.trips.deleteTrip);
  const [deletingId, setDeletingId] = useState(null);
  const [showActionsFor, setShowActionsFor] = useState(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showActionsFor && !event.target.closest('.actions-menu')) {
        setShowActionsFor(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showActionsFor]);

  const handleDelete = async (tripId) => {
    if (window.confirm('Are you sure you want to delete this trip?')) {
      setDeletingId(tripId);
      try {
        await deleteTrip({ id: tripId });
      } catch (error) {
        console.error('Error deleting trip:', error);
        alert('Failed to delete trip. Please try again.');
      } finally {
        setDeletingId(null);
        setShowActionsFor(null);
      }
    }
  };

  const handleOpen = (trip) => {
    // Store trip data and navigate to itinerary view
    localStorage.setItem('tripData', JSON.stringify({
      destination: trip.destination,
      dates: `${trip.startDate} to ${trip.endDate}`,
      travelers: trip.travelers,
      departureCities: trip.departureCities || []
    }));
    localStorage.setItem('savedItinerary', JSON.stringify(trip.itineraryData));
    navigate('/itinerary');
  };

  const handleEdit = (trip) => {
    // Navigate to landing page with pre-filled form
    navigate('/', { state: { editingTrip: trip } });
  };

  if (!trips) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading your trips...</p>
      </div>
    );
  }

  if (trips.length === 0) {
    return (
      <div className="text-center py-12">
        <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No trips yet</h3>
        <p className="text-gray-600">Start planning your next adventure!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Your Trips</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trips.map((trip, index) => (
          <motion.div
            key={trip._id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:shadow-lg transition-shadow relative group">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-blue-600" />
                    {trip.destination}
                  </CardTitle>
                  
                  {/* Actions Menu */}
                  <div className="relative actions-menu">
                    <button
                      onClick={() => setShowActionsFor(showActionsFor === trip._id ? null : trip._id)}
                      className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <MoreVertical className="w-4 h-4 text-gray-600" />
                    </button>
                    
                    {showActionsFor === trip._id && (
                      <div className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border z-10">
                        <button
                          onClick={() => handleOpen(trip)}
                          className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                        >
                          <Eye className="w-4 h-4" />
                          View Itinerary
                        </button>
                        <button
                          onClick={() => handleEdit(trip)}
                          className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                        >
                          <Edit className="w-4 h-4" />
                          Edit Trip
                        </button>
                        <button
                          onClick={() => handleDelete(trip._id)}
                          disabled={deletingId === trip._id}
                          className="w-full px-4 py-2 text-left text-sm hover:bg-red-50 text-red-600 flex items-center gap-2 disabled:opacity-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          {deletingId === trip._id ? 'Deleting...' : 'Delete Trip'}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {trip.startDate}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {trip.travelers}
                  </span>
                </div>
                
                {trip.tripType && (
                  <Badge variant="outline" className="text-xs">
                    {trip.tripType}
                  </Badge>
                )}
                
                {trip.itineraryData && (
                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-500 mb-2">
                      Saved itinerary with booking options
                    </p>
                    
                    {/* Show booking stats if available */}
                    {trip.bookingValidation && (
                      <div className="flex gap-2 text-xs">
                        {trip.bookingValidation.has_flight_bookings && (
                          <Badge className="bg-green-100 text-green-800">Flights</Badge>
                        )}
                        {trip.bookingValidation.has_hotel_bookings && (
                          <Badge className="bg-blue-100 text-blue-800">Hotels</Badge>
                        )}
                        {trip.bookingValidation.has_restaurant_bookings && (
                          <Badge className="bg-orange-100 text-orange-800">Dining</Badge>
                        )}
                        {trip.bookingValidation.has_activity_bookings && (
                          <Badge className="bg-purple-100 text-purple-800">Activities</Badge>
                        )}
                      </div>
                    )}
                  </div>
                )}
                
                <div className="text-xs text-gray-400">
                  Saved {new Date(trip.createdAt).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}