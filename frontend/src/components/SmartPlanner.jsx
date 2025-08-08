import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, MapPin, Users, Clock, CheckCircle, Sparkles, X } from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useLocation } from 'react-router-dom';
import { api } from '../utils/api';
import { useUser } from '@clerk/clerk-react';
import { useMutation, useQuery } from 'convex/react';
import { api as convexApi } from '../../convex/_generated/api';
import ConfettiEffect from './ui/ConfettiEffect';
import WeatherCard from './WeatherCard';
import SlotCard from './SlotCard';
import ChatInterface from './ChatInterface';
import MapJourney from './MapJourney';
import DailyPlannerView from './DailyPlannerView';

const SmartPlanner = () => {
  const location = useLocation();
  const { user } = useUser();
  const currentUser = useQuery(convexApi.users.getMyUser);
  const saveItinerary = useMutation(convexApi.richItineraries.saveFromBackend);
  const updateSlotCompletion = useMutation(convexApi.richItineraries.updateSlotCompletion);
  
  // Load saved itineraries
  const savedItineraries = useQuery(convexApi.richItineraries.getUserItineraries, 
    currentUser?._id ? { userId: currentUser._id } : "skip"
  );
  const activeItinerary = useQuery(convexApi.richItineraries.getActiveItinerary,
    currentUser?._id ? { userId: currentUser._id } : "skip"
  );
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
  const [showForm, setShowForm] = useState(true);
  const [toast, setToast] = useState(null);

  // Load saved itinerary on mount if exists
  useEffect(() => {
    if (activeItinerary && !itinerary) {
      // Transform saved itinerary to match expected format
      const transformed = {
        ...activeItinerary,
        status: 'success',
        itinerary_id: activeItinerary.itineraryId,
        destination: activeItinerary.destination,
        start_date: activeItinerary.startDate,
        end_date: activeItinerary.endDate,
        duration_days: activeItinerary.durationDays,
        travelers: activeItinerary.travelers,
        total_budget: activeItinerary.totalBudget,
        interests: activeItinerary.interests,
        pace: activeItinerary.pace,
        daily_plans: activeItinerary.dailyPlans,
        recommendations: activeItinerary.recommendations,
        ai_analysis: activeItinerary.aiAnalysis,
        export_format: activeItinerary.exportFormat,
        journey_data: activeItinerary.journeyData
      };
      setItinerary(transformed);
      setShowForm(false);
    }
  }, [activeItinerary]);
  
  // Check for incoming trip data from navigation
  useEffect(() => {
    if (location.state?.tripData) {
      const tripData = location.state.tripData;
      setPlannerData(prev => ({
        ...prev,
        destination: tripData.destination || '',
        travelers: tripData.travelers || 1,
        startDate: tripData.startDate || '',
        endDate: tripData.endDate || ''
      }));
    }
  }, [location.state]);

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
      console.log('API Response:', result); // Debug log
      
      if (result && result.status === 'success' && result.daily_plans && result.daily_plans.length > 0) {
        setItinerary(result);
        setShowForm(false);
        
        // Auto-save to Convex if user is authenticated
        if (currentUser?._id) {
          try {
            // Transform journey_data field names from snake_case to camelCase
            const transformedJourneyData = result.journey_data ? {
              totalActivities: result.journey_data.total_activities || result.journey_data.totalActivities || 0,
              completed: result.journey_data.completed || 0,
              progressPercentage: result.journey_data.progress_percentage || result.journey_data.progressPercentage || 0,
              levels: result.journey_data.levels || 1,
              currentLevel: result.journey_data.current_level || result.journey_data.currentLevel || 1,
              badges: result.journey_data.badges || []
            } : {
              totalActivities: result.daily_plans?.length * 4 || 0,
              completed: 0,
              progressPercentage: 0,
              levels: result.duration_days || 1,
              currentLevel: 1,
              badges: []
            };

            await saveItinerary({
              userId: currentUser._id,
              itineraryData: {
                itineraryId: result.itinerary_id,
                destination: result.destination,
                startDate: result.start_date,
                endDate: result.end_date,
                durationDays: result.duration_days,
                travelers: result.travelers,
                totalBudget: result.total_budget,
                interests: result.interests,
                pace: result.pace,
                dailyPlans: result.daily_plans,
                recommendations: result.recommendations,
                aiAnalysis: result.ai_analysis,
                exportFormat: result.export_format,
                journeyData: transformedJourneyData
              }
            });
            console.log('Itinerary auto-saved to Convex');
          } catch (saveError) {
            console.error('Failed to auto-save itinerary:', saveError);
          }
        }
      } else if (result && result.status === 'success') {
        // API returned success but no plans
        throw new Error('Itinerary generated but no daily plans were created. Please try again.');
      } else {
        throw new Error(result?.message || 'Failed to generate itinerary');
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
      // Mark slot as completed locally
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
      
      // Update in Convex if we have an itinerary ID
      if (itinerary?.itinerary_id) {
        try {
          const result = await updateSlotCompletion({
            itineraryId: itinerary.itinerary_id,
            dayIndex,
            slotIndex,
            completed: true
          });
          
          // Update journey data from Convex response
          if (result?.journeyData) {
            setItinerary(prev => ({
              ...prev,
              journey_data: result.journeyData
            }));
          }
        } catch (convexError) {
          console.error('Failed to update slot in Convex:', convexError);
        }
      }
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

  // Show toast notification
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Save itinerary manually
  const saveItineraryManual = async () => {
    if (!itinerary || !currentUser?._id) {
      showToast('Please sign in to save your itinerary', 'error');
      return;
    }

    try {
      // Save to Convex
      await saveItinerary({
        userId: currentUser._id,
        itineraryData: {
          itineraryId: itinerary.itinerary_id,
          destination: itinerary.destination || plannerData.destination,
          startDate: itinerary.start_date || plannerData.startDate,
          endDate: itinerary.end_date || plannerData.endDate,
          durationDays: itinerary.duration_days,
          travelers: itinerary.travelers || plannerData.travelers,
          totalBudget: itinerary.total_budget || plannerData.budget,
          interests: itinerary.interests || plannerData.interests,
          pace: itinerary.pace || 'moderate',
          dailyPlans: itinerary.daily_plans,
          recommendations: itinerary.recommendations || { flights: [], hotels: [], restaurants: [], activities: [] },
          aiAnalysis: itinerary.ai_analysis || '',
          exportFormat: itinerary.export_format || { version: '1.0', type: 'travelai_itinerary', exportable: true },
          journeyData: itinerary.journey_data || {
            totalActivities: itinerary.daily_plans?.reduce((t, d) => t + d.slots.length, 0) || 0,
            completed: completedSlots.size,
            progressPercentage: 0,
            levels: itinerary.daily_plans?.length || 1,
            currentLevel: 1,
            badges: []
          }
        }
      });
      
      showToast('Itinerary saved successfully!', 'success');
    } catch (error) {
      console.error('Failed to save itinerary:', error);
      showToast('Failed to save itinerary', 'error');
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

        {/* Show saved itineraries if available */}
        {savedItineraries && savedItineraries.length > 0 && !itinerary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl p-6 mb-8"
          >
            <h3 className="text-xl font-bold text-gray-800 mb-4">Your Saved Itineraries</h3>
            <div className="space-y-3">
              {savedItineraries.slice(0, 3).map((saved) => (
                <div key={saved._id} className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                     onClick={() => {
                       const transformed = {
                         ...saved,
                         status: 'success',
                         itinerary_id: saved.itineraryId,
                         destination: saved.destination,
                         start_date: saved.startDate,
                         end_date: saved.endDate,
                         duration_days: saved.durationDays,
                         travelers: saved.travelers,
                         total_budget: saved.totalBudget,
                         interests: saved.interests,
                         pace: saved.pace,
                         daily_plans: saved.dailyPlans,
                         recommendations: saved.recommendations,
                         ai_analysis: saved.aiAnalysis,
                         export_format: saved.exportFormat,
                         journey_data: saved.journeyData
                       };
                       setItinerary(transformed);
                       setShowForm(false);
                     }}>
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-semibold text-gray-700">{saved.destination}</h4>
                      <p className="text-sm text-gray-500">
                        {saved.startDate} to {saved.endDate} • {saved.travelers} travelers
                      </p>
                    </div>
                    <div className="text-sm text-gray-400">
                      {saved.isActive && <span className="text-green-600 font-semibold">Active</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Planning Form */}
        {(!itinerary || !itinerary.daily_plans || itinerary.daily_plans.length === 0) && showForm && (
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
                  onChange={(e) => handleInputChange('travelers', parseInt(e.target.value) || 1)}
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

        {/* Clear any broken state */}
        {itinerary && (!itinerary.daily_plans || itinerary.daily_plans.length === 0) && (
          <script>{(() => { setItinerary(null); })()}</script>
        )}

        {/* Itinerary Display */}
        {itinerary && itinerary.daily_plans && itinerary.daily_plans.length > 0 && (
          <div className="space-y-8">
            {/* Itinerary Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-800">
                  Your Trip to {itinerary.destination || plannerData.destination}
                </h2>
                <button
                  onClick={saveItineraryManual}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Save Itinerary
                </button>
              </div>
              <div className="flex items-center gap-4 text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {itinerary.start_date || plannerData.startDate} to {itinerary.end_date || plannerData.endDate}
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

            {/* Reset Button if no valid itinerary */}
            {(!itinerary.daily_plans || itinerary.daily_plans.length === 0) && (
              <button
                onClick={() => {
                  setItinerary(null);
                  setShowForm(true);
                  setError(null);
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create New Itinerary
              </button>
            )}

            {/* Itinerary Plan Display - Legacy Support */}
            {itinerary && itinerary.plan && !itinerary.daily_plans && (
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

      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: -50, x: '-50%' }}
            className="fixed top-8 left-1/2 z-50"
          >
            <div className={`flex items-center gap-3 px-6 py-4 rounded-xl shadow-2xl ${
              toast.type === 'success' 
                ? 'bg-gradient-to-r from-green-500 to-green-600 text-white' 
                : 'bg-gradient-to-r from-red-500 to-red-600 text-white'
            }`}>
              {toast.type === 'success' ? (
                <CheckCircle className="w-6 h-6" />
              ) : (
                <X className="w-6 h-6" />
              )}
              <span className="font-medium text-lg">{toast.message}</span>
              <button
                onClick={() => setToast(null)}
                className="ml-4 p-1 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SmartPlanner;