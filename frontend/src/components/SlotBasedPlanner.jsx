import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { 
  Plus, 
  Clock, 
  MapPin, 
  CheckCircle, 
  Circle, 
  Trash2, 
  Edit3,
  Sun,
  Sunset,
  Moon,
  Star,
  Calendar,
  Users,
  Target
} from 'lucide-react';
import { useCurrentUser } from '../hooks/useCurrentUser';

const SlotBasedPlanner = ({ tripId, date }) => {
  const { user } = useCurrentUser();
  const [selectedDate, setSelectedDate] = useState(date || new Date().toISOString().split('T')[0]);
  const [slots, setSlots] = useState([]);
  const [isAddingSlot, setIsAddingSlot] = useState(false);
  const [editingSlot, setEditingSlot] = useState(null);
  const [newSlot, setNewSlot] = useState({
    timeSlot: 'morning',
    activity: '',
    location: '',
    duration: 60
  });

  const timeSlotConfig = {
    morning: { 
      icon: Sun, 
      color: 'bg-yellow-100 border-yellow-300 text-yellow-800',
      time: '6:00 AM - 12:00 PM',
      emoji: '🌅'
    },
    midday: { 
      icon: Sun, 
      color: 'bg-orange-100 border-orange-300 text-orange-800',
      time: '12:00 PM - 5:00 PM',
      emoji: '☀️'
    },
    evening: { 
      icon: Sunset, 
      color: 'bg-purple-100 border-purple-300 text-purple-800',
      time: '5:00 PM - 9:00 PM',
      emoji: '🌅'
    },
    night: { 
      icon: Moon, 
      color: 'bg-blue-100 border-blue-300 text-blue-800',
      time: '9:00 PM - 12:00 AM',
      emoji: '🌙'
    }
  };

  useEffect(() => {
    loadSlots();
  }, [selectedDate, tripId]);

  const loadSlots = async () => {
    try {
      const response = await fetch(`/api/slots/trip/${tripId || 'default'}`);
      const data = await response.json();
      if (data.status === 'success') {
        setSlots(data.slots || []);
      }
    } catch (error) {
      console.error('Error loading slots:', error);
    }
  };

  const handleAddSlot = async () => {
    try {
      const response = await fetch('/api/slots/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trip_id: tripId || 'default',
          day: 1,
          time_slot: newSlot.timeSlot,
          activity: newSlot.activity,
          location: newSlot.location,
          duration: newSlot.duration
        })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        setSlots([...slots, { ...data.slot, id: `slot_${Date.now()}` }]);
        setNewSlot({ timeSlot: 'morning', activity: '', location: '', duration: 60 });
        setIsAddingSlot(false);
      }
    } catch (error) {
      console.error('Error adding slot:', error);
    }
  };

  const handleCompleteSlot = async (slotId) => {
    try {
      const response = await fetch(`/api/slots/${slotId}/complete`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        setSlots(slots.map(slot => 
          slot.id === slotId 
            ? { ...slot, status: 'completed', completedAt: new Date().toISOString() }
            : slot
        ));
        
        if (data.celebration) {
          window.dispatchEvent(new CustomEvent('celebrate', { 
            detail: { message: 'You did it! 🎉', type: 'slot-complete' }
          }));
        }
      }
    } catch (error) {
      console.error('Error completing slot:', error);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(slots);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setSlots(items);
  };

  const getCompletedCount = () => {
    return slots.filter(slot => slot.status === 'completed').length;
  };

  const getProgressPercentage = () => {
    return slots.length > 0 ? (getCompletedCount() / slots.length) * 100 : 0;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-6 mb-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Smart Daily Planner</h1>
              <p className="text-gray-600">Plan your perfect day with AI-powered slot management</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">{getCompletedCount()}/{slots.length}</div>
              <div className="text-sm text-gray-500">Slots Completed</div>
            </div>
          </div>

          <div className="flex items-center gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex-1 bg-gray-200 rounded-full h-3">
              <motion.div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${getProgressPercentage()}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            
            <button
              onClick={() => setIsAddingSlot(true)}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Slot
            </button>
          </div>
        </motion.div>

        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="slots">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef} className="space-y-4">
                <AnimatePresence>
                  {slots.map((slot, index) => {
                    const config = timeSlotConfig[slot.time_slot] || timeSlotConfig.morning;
                    const IconComponent = config.icon;
                    
                    return (
                      <Draggable key={slot.id} draggableId={slot.id} index={index}>
                        {(provided, snapshot) => (
                          <motion.div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className={`bg-white rounded-xl shadow-lg p-6 border-2 ${config.color} ${
                              snapshot.isDragging ? 'rotate-2 scale-105' : ''
                            } transition-all duration-200`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-4 flex-1">
                                <div className="text-3xl">{config.emoji}</div>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <h3 className="text-lg font-semibold text-gray-800">
                                      {slot.activity}
                                    </h3>
                                    <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                      {slot.time_slot}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <div className="flex items-center gap-1">
                                      <Clock className="w-4 h-4" />
                                      {config.time}
                                    </div>
                                    {slot.location && (
                                      <div className="flex items-center gap-1">
                                        <MapPin className="w-4 h-4" />
                                        {slot.location}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleCompleteSlot(slot.id)}
                                  className={`p-2 rounded-full transition-colors ${
                                    slot.status === 'completed'
                                      ? 'bg-green-100 text-green-600'
                                      : 'bg-gray-100 text-gray-400 hover:bg-green-100 hover:text-green-600'
                                  }`}
                                >
                                  {slot.status === 'completed' ? (
                                    <CheckCircle className="w-5 h-5" />
                                  ) : (
                                    <Circle className="w-5 h-5" />
                                  )}
                                </button>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </Draggable>
                    );
                  })}
                </AnimatePresence>
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

        <AnimatePresence>
          {isAddingSlot && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            >
              <div className="bg-white rounded-2xl p-6 w-full max-w-md">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Add New Slot</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Time Slot</label>
                    <select
                      value={newSlot.timeSlot}
                      onChange={(e) => setNewSlot({ ...newSlot, timeSlot: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="morning">🌅 Morning (6AM - 12PM)</option>
                      <option value="midday">☀️ Midday (12PM - 5PM)</option>
                      <option value="evening">🌅 Evening (5PM - 9PM)</option>
                      <option value="night">🌙 Night (9PM - 12AM)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Activity</label>
                    <input
                      type="text"
                      value={newSlot.activity}
                      onChange={(e) => setNewSlot({ ...newSlot, activity: e.target.value })}
                      placeholder="What would you like to do?"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                    <input
                      type="text"
                      value={newSlot.location}
                      onChange={(e) => setNewSlot({ ...newSlot, location: e.target.value })}
                      placeholder="Where will this happen?"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={() => setIsAddingSlot(false)}
                    className="flex-1 px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddSlot}
                    disabled={!newSlot.activity}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Add Slot
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SlotBasedPlanner;
