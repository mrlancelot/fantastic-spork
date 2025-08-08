import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Plane, Compass, Star } from 'lucide-react';

const MapJourney = ({ destination, completedSlots, totalSlots }) => {
  const [progress, setProgress] = useState(0);
  const [currentLocation, setCurrentLocation] = useState(0);

  useEffect(() => {
    const progressPercent = totalSlots > 0 ? (completedSlots / totalSlots) * 100 : 0;
    setProgress(progressPercent);
    setCurrentLocation(Math.floor((progressPercent / 100) * 10)); // 10 locations on the journey
  }, [completedSlots, totalSlots]);

  const journeyPoints = [
    { id: 0, name: "Home", emoji: "🏠", x: 10, y: 80 },
    { id: 1, name: "Airport", emoji: "✈️", x: 25, y: 65 },
    { id: 2, name: "Mountains", emoji: "🏔️", x: 40, y: 45 },
    { id: 3, name: "Forest", emoji: "🌲", x: 55, y: 35 },
    { id: 4, name: "Desert", emoji: "🏜️", x: 70, y: 25 },
    { id: 5, name: "Ocean", emoji: "🌊", x: 85, y: 15 },
    { id: 6, name: "Island", emoji: "🏝️", x: 90, y: 30 },
    { id: 7, name: "City", emoji: "🏙️", x: 80, y: 50 },
    { id: 8, name: "Castle", emoji: "🏰", x: 65, y: 70 },
    { id: 9, name: destination, emoji: "🎯", x: 50, y: 85 }
  ];

  const pathData = journeyPoints.map((point, index) => {
    if (index === 0) return `M ${point.x} ${point.y}`;
    return `L ${point.x} ${point.y}`;
  }).join(' ');

  return (
    <div className="relative w-full h-96 bg-gradient-to-br from-blue-200 via-green-200 to-yellow-200 rounded-2xl overflow-hidden shadow-xl">
      {/* Background Clouds */}
      <div className="absolute inset-0">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-6xl opacity-30"
            animate={{
              x: [0, 50, 0],
              y: [0, -20, 0],
            }}
            transition={{
              duration: 8 + i * 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{
              left: `${15 + i * 20}%`,
              top: `${10 + i * 10}%`
            }}
          >
            ☁️
          </motion.div>
        ))}
      </div>

      {/* SVG Path */}
      <svg className="absolute inset-0 w-full h-full">
        {/* Journey Path */}
        <motion.path
          d={pathData}
          fill="none"
          stroke="#4F46E5"
          strokeWidth="4"
          strokeDasharray="10,5"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: progress / 100 }}
          transition={{ duration: 1, ease: "easeInOut" }}
          className="drop-shadow-lg"
        />
        
        {/* Completed Path */}
        <motion.path
          d={pathData}
          fill="none"
          stroke="#10B981"
          strokeWidth="6"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: progress / 100 }}
          transition={{ duration: 1, ease: "easeInOut" }}
          className="opacity-60"
        />
      </svg>

      {/* Journey Points */}
      {journeyPoints.map((point, index) => {
        const isCompleted = index <= currentLocation;
        const isActive = index === currentLocation;
        
        return (
          <motion.div
            key={point.id}
            className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer ${
              isActive ? 'z-20' : 'z-10'
            }`}
            style={{ left: `${point.x}%`, top: `${point.y}%` }}
            initial={{ scale: 0 }}
            animate={{ scale: isCompleted ? 1 : 0.6 }}
            whileHover={{ scale: isCompleted ? 1.2 : 0.8 }}
            transition={{ delay: index * 0.1 }}
          >
            {/* Point Circle */}
            <div className={`relative w-12 h-12 rounded-full flex items-center justify-center shadow-lg border-4 transition-all duration-300 ${
              isCompleted 
                ? 'bg-green-400 border-green-600' 
                : 'bg-gray-300 border-gray-400'
            }`}>
              <span className="text-xl">{point.emoji}</span>
              
              {/* Active Pulse */}
              {isActive && (
                <motion.div
                  className="absolute inset-0 rounded-full bg-yellow-400 border-4 border-yellow-600"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [1, 0, 1]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
              
              {/* Completion Star */}
              {isCompleted && index < currentLocation && (
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  className="absolute -top-1 -right-1 text-yellow-400"
                >
                  <Star className="w-4 h-4 fill-current" />
                </motion.div>
              )}
            </div>
            
            {/* Point Label */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: isCompleted ? 1 : 0.6, y: 0 }}
              className="absolute top-14 left-1/2 transform -translate-x-1/2 text-center"
            >
              <span className={`text-xs font-medium px-2 py-1 rounded-full shadow-sm ${
                isCompleted 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {point.name}
              </span>
            </motion.div>
          </motion.div>
        );
      })}

      {/* Traveling Character */}
      <motion.div
        className="absolute z-30 text-4xl"
        animate={{
          left: `${journeyPoints[currentLocation]?.x || 0}%`,
          top: `${journeyPoints[currentLocation]?.y || 0}%`,
        }}
        transition={{ duration: 1.5, ease: "easeInOut" }}
        style={{ transform: 'translate(-50%, -50%)' }}
      >
        <motion.div
          animate={{ 
            rotate: [0, 10, 0, -10, 0],
            y: [0, -5, 0, -5, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          🚀
        </motion.div>
      </motion.div>

      {/* Progress Info */}
      <div className="absolute top-4 left-4 bg-white bg-opacity-90 rounded-lg p-3 shadow-lg">
        <div className="flex items-center gap-2 mb-2">
          <Compass className="w-5 h-5 text-blue-600" />
          <span className="font-semibold text-gray-800">Journey Progress</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1 }}
            />
          </div>
          <span className="text-sm font-medium text-gray-700">
            {Math.round(progress)}%
          </span>
        </div>
        <p className="text-xs text-gray-600 mt-1">
          {completedSlots} of {totalSlots} activities completed
        </p>
      </div>

      {/* Destination Info */}
      <div className="absolute bottom-4 right-4 bg-white bg-opacity-90 rounded-lg p-3 shadow-lg">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-purple-600" />
          <div>
            <p className="font-semibold text-gray-800">{destination}</p>
            <p className="text-xs text-gray-600">
              {currentLocation === journeyPoints.length - 1 ? 'Arrived!' : 'En route...'}
            </p>
          </div>
        </div>
      </div>

      {/* Celebration Particles */}
      {progress === 100 && (
        <div className="absolute inset-0">
          {[...Array(10)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute text-2xl"
              initial={{ 
                x: '50%', 
                y: '50%', 
                opacity: 1,
                scale: 0
              }}
              animate={{
                x: `${50 + (Math.random() - 0.5) * 200}%`,
                y: `${50 + (Math.random() - 0.5) * 200}%`,
                opacity: 0,
                scale: 1
              }}
              transition={{
                duration: 2,
                delay: i * 0.1,
                ease: "easeOut"
              }}
            >
              {['🎉', '🎊', '⭐', '🌟'][i % 4]}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MapJourney;