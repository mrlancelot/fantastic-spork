import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, MapPin, Users, Clock, CheckCircle, Sparkles } from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { api } from '../utils/api';
import ConfettiEffect from './ui/ConfettiEffect';
import WeatherCard from './WeatherCard';
import SlotCard from './SlotCard';
import ChatInterface from './ChatInterface';
import MapJourney from './MapJourney';
import DailyPlannerView from './DailyPlannerView';

const SmartPlanner = () => {
  const [plannerData, setPlannerData] = useState({
    destination: '',
    startDate: '',
    endDate: '',
    travelers: 1,
    interests: [],
    budget: 1000
  });

  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const [completedSlots, setCompletedSlots] = useState(new Set());
  const [error, setError] = useState(null);

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setPlannerData(prev => ({ ...prev, [field]: value }));
  };

  // Create smart itinerary
  const createItinerary = async () => {
    if (!plannerData.destination || !plannerData.startDate || !plannerData.endDate) {
      setError('Please fill in destination and dates');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.smartPlanner.create(
        plannerData.destination,
        plannerData.startDate,
        plannerData.endDate,
        plannerData.travelers,
        plannerData.interests,
        plannerData.budget
      );

      // The API returns the itinerary data directly, not nested
      if (result && result.status === 'success') {
        setItinerary(result);
      } else {
        throw new Error('Failed to generate itinerary');
      }
    } catch (error) {
      setError(`Failed to create itinerary: ${error.message}`);
      console.error('Itinerary creation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle slot completion
  const handleSlotComplete = async (slotId, dayIndex, slotIndex) => {
    try {
      await api.completeSlot(slotId);
      
      // Mark slot as completed
      setCompletedSlots(prev => new Set([...prev, slotId]));
      
      // Trigger confetti celebration
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
      
      // Update itinerary state
      setItinerary(prev => {
        const updated = { ...prev };
        updated.daily_plans[dayIndex].slots[slotIndex].completed = true;
        return updated;
      });
    } catch (error) {
      console.error('Failed to complete slot:', error);
    }
  };

  // Handle drag and drop reordering
  const handleDragEnd = (result, dayIndex) => {
    if (!result.destination) return;

    const { source, destination } = result;
    
    if (source.index === destination.index) return;

    // Reorder slots within the same day
    setItinerary(prev => {
      const updated = { ...prev };
      const daySlots = [...updated.daily_plans[dayIndex].slots];
      const [removed] = daySlots.splice(source.index, 1);
      daySlots.splice(destination.index, 0, removed);
      updated.daily_plans[dayIndex].slots = daySlots;
      return updated;
    });
  };

  // Save itinerary
  const saveItinerary = async () => {
    if (!itinerary) return;

    try {
      const result = await api.saveItinerary({
        ...itinerary,
        user_id: 'current-user', // Replace with actual user ID from auth
        ...plannerData
      });
      
      alert('Itinerary saved successfully!');
    } catch (error) {
      console.error('Failed to save itinerary:', error);
      alert('Failed to save itinerary');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <ConfettiEffect show={showConfetti} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-800 mb-2 flex items-center justify-center gap-2">
            <Sparkles className="text-purple-600" />
            Smart Daily Planner
          </h1>
          <p className="text-lg text-gray-600">Plan your perfect trip with AI-powered recommendations</p>
        </motion.div>

        {/* Planning Form */}
        {!itinerary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8 mb-8"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <MapPin className="inline w-4 h-4 mr-1" />
                  Destination
                </label>
                <input
                  type="text"
                  placeholder="Where are you going?"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={plannerData.destination}
                  onChange={(e) => handleInputChange('destination', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Users className="inline w-4 h-4 mr-1" />
                  Travelers
                </label>
                <input
                  type="number"
                  min="1"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={plannerData.travelers}
                  onChange={(e) => handleInputChange('travelers', parseInt(e.target.value))}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Calendar className="inline w-4 h-4 mr-1" />
                  Start Date
                </label>
                <input
                  type="date"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={plannerData.startDate}
                  onChange={(e) => handleInputChange('startDate', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <Calendar className="inline w-4 h-4 mr-1" />
                  End Date
                </label>
                <input
                  type="date"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={plannerData.endDate}
                  onChange={(e) => handleInputChange('endDate', e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {error}
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={createItinerary}
              disabled={loading}
              className="w-full mt-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Your Perfect Itinerary...' : 'Create Smart Itinerary'}
            </motion.button>
          </motion.div>
        )}

        {/* Itinerary Display */}
        {itinerary && (
          <div className="space-y-8">
            {/* Itinerary Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-800">
                  Your Trip to {itinerary.destination}
                </h2>
                <button
                  onClick={saveItinerary}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Save Itinerary
                </button>
              </div>
              <div className="flex items-center gap-4 text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {itinerary.start_date} to {itinerary.end_date}
                </span>
                {plannerData.travelers && (
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {plannerData.travelers} traveler{plannerData.travelers > 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </motion.div>

            {/* Map Journey Visualization */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <MapJourney 
                destination={itinerary.destination}
                completedSlots={completedSlots.size}
                totalSlots={itinerary.daily_plans?.reduce((total, day) => total + day.slots.length, 0) || 0}
              />
            </motion.div>

            {/* Itinerary Plan Display */}
            {itinerary.plan && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-2xl shadow-lg p-8"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-4">Your Itinerary</h3>
                <div className="prose prose-lg max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700">
                    {itinerary.plan}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Daily Plans (if available) */}
            <div className="space-y-6">
              {itinerary.daily_plans?.map((day, dayIndex) => (
                <motion.div
                  key={day.date}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: dayIndex * 0.1 }}
                  className="bg-white rounded-2xl shadow-lg overflow-hidden"
                >
                  {/* Day Header */}
                  <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
                    <div className="flex justify-between items-center">
                      <h3 className="text-xl font-bold">
                        Day {dayIndex + 1} - {new Date(day.date).toLocaleDateString('en-US', { 
                          weekday: 'long', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </h3>
                      {day.weather && <WeatherCard weather={day.weather} />}
                    </div>
                  </div>

                  {/* Time Slots with DnD Kit */}
                  <DailyPlannerView 
                    day={day} 
                    dayIndex={dayIndex} 
                    onSlotComplete={handleSlotComplete}
                    completedSlots={completedSlots}
                    onDragEnd={(activeId, overId) => {
                      if (activeId !== overId) {
                        const oldIndex = day.slots.findIndex(s => s.id === activeId);
                        const newIndex = day.slots.findIndex(s => s.id === overId);
                        handleDragEnd({ source: { index: oldIndex }, destination: { index: newIndex } }, dayIndex);
                      }
                    }}
                  />
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Chat Interface */}
        <ChatInterface />
      </div>
    </div>
  );
};

export default SmartPlanner;