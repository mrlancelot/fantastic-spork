import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { useConfetti } from '../contexts/ConfettiContext';

export default function ConfettiToggle() {
  const { confettiEnabled, toggleConfetti } = useConfetti();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed bottom-4 right-4 z-50"
    >
      <button
        onClick={toggleConfetti}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-full shadow-lg
          transition-all duration-300 hover:scale-105
          ${confettiEnabled 
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
            : 'bg-gray-200 text-gray-600'
          }
        `}
        title={confettiEnabled ? 'Disable Confetti' : 'Enable Confetti'}
      >
        <Sparkles 
          className={`w-5 h-5 ${confettiEnabled ? 'animate-pulse' : ''}`} 
        />
        <span className="text-sm font-medium">
          {confettiEnabled ? 'Confetti ON' : 'Confetti OFF'}
        </span>
      </button>
    </motion.div>
  );
}