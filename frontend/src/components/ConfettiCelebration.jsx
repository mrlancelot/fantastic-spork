import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ConfettiCelebration = () => {
  const [celebrations, setCelebrations] = useState([]);

  useEffect(() => {
    const handleCelebrate = (event) => {
      const { message, type } = event.detail;
      const id = Date.now();
      
      setCelebrations(prev => [...prev, { id, message, type }]);
      
      setTimeout(() => {
        setCelebrations(prev => prev.filter(c => c.id !== id));
      }, 4000);
    };

    window.addEventListener('celebrate', handleCelebrate);
    return () => window.removeEventListener('celebrate', handleCelebrate);
  }, []);

  const generateConfetti = () => {
    return Array.from({ length: 50 }, (_, i) => (
      <motion.div
        key={i}
        className="absolute w-2 h-2 rounded-full"
        style={{
          backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'][i % 6],
          left: `${Math.random() * 100}%`,
          top: '-10px'
        }}
        initial={{ y: -10, rotate: 0, opacity: 1 }}
        animate={{
          y: window.innerHeight + 100,
          rotate: 360,
          opacity: 0,
          x: Math.random() * 200 - 100
        }}
        transition={{
          duration: 3 + Math.random() * 2,
          ease: 'easeOut',
          delay: Math.random() * 0.5
        }}
      />
    ));
  };

  return (
    <AnimatePresence>
      {celebrations.map(celebration => (
        <motion.div
          key={celebration.id}
          className="fixed inset-0 pointer-events-none z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {generateConfetti()}
          
          <motion.div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 180 }}
            transition={{ type: 'spring', damping: 15, stiffness: 300 }}
          >
            <div className="bg-white rounded-2xl shadow-2xl p-8 text-center border-4 border-yellow-400">
              <motion.div
                className="text-6xl mb-4"
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ repeat: Infinity, duration: 0.5 }}
              >
                🎉
              </motion.div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">
                {celebration.message}
              </h2>
              <p className="text-gray-600">
                {celebration.type === 'slot-complete' && 'Slot completed successfully!'}
                {celebration.type === 'day-complete' && 'Amazing! You completed your entire day!'}
                {celebration.type === 'achievement' && 'New achievement unlocked!'}
              </p>
            </div>
          </motion.div>
        </motion.div>
      ))}
    </AnimatePresence>
  );
};

export default ConfettiCelebration;
