import { motion } from 'framer-motion';
import { Clock, MapPin, CheckCircle, Circle, ExternalLink } from 'lucide-react';

const timeSlotConfig = {
  morning: { 
    color: 'from-yellow-400 to-orange-500', 
    icon: '🌅', 
    bgColor: 'bg-yellow-50 border-yellow-200' 
  },
  midday: { 
    color: 'from-blue-400 to-blue-600', 
    icon: '☀️', 
    bgColor: 'bg-blue-50 border-blue-200' 
  },
  evening: { 
    color: 'from-purple-500 to-pink-500', 
    icon: '🌆', 
    bgColor: 'bg-purple-50 border-purple-200' 
  },
  night: { 
    color: 'from-indigo-600 to-purple-700', 
    icon: '🌙', 
    bgColor: 'bg-indigo-50 border-indigo-200' 
  }
};

const SlotCard = ({ slot, slotIndex, onComplete, completed }) => {
  const config = timeSlotConfig[slot.timeSlot || slot.time_slot] || timeSlotConfig.midday;
  
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      className={`border-2 rounded-xl p-4 ${config.bgColor} ${completed ? 'opacity-75' : ''} transition-all duration-300`}
    >
      <div className="flex items-center justify-between mb-3">
        {/* Time Slot Header */}
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${config.color} flex items-center justify-center text-white font-bold text-sm`}>
            <span className="text-lg">{config.icon}</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 capitalize">
              {slot.timeSlot || slot.time_slot}
            </h4>
            <p className="text-sm text-gray-600 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {slot.duration}
            </p>
          </div>
        </div>

        {/* Completion Button */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => !completed && onComplete()}
          disabled={completed}
          className={`p-2 rounded-full transition-all ${
            completed 
              ? 'text-green-600 bg-green-100' 
              : 'text-gray-400 hover:text-green-600 hover:bg-green-100'
          }`}
        >
          {completed ? <CheckCircle className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
        </motion.button>
      </div>

      {/* Activity Content */}
      <div className="space-y-2">
        <h5 className="font-medium text-gray-800">
          {slot.title || slot.activity}
        </h5>
        <p className="text-sm text-gray-600">
          {slot.description}
        </p>
        
        {slot.location && (
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {slot.location}
          </p>
        )}

        {slot.booking_url && (
          <a
            href={slot.booking_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ExternalLink className="w-3 h-3" />
            Book Now
          </a>
        )}
      </div>

      {/* Completion Badge */}
      {completed && (
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-3 flex justify-center"
        >
          <div className="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
            <span>Completed!</span> 
            <span>🎉</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default SlotCard;