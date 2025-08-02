import { motion, AnimatePresence } from 'framer-motion';
import { Info, X } from 'lucide-react';
import { useEffect } from 'react';
import { cn } from '../../utils/cn';

export function Toast({ message, onClose, duration = 3000, className }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.9 }}
        className={cn(
          "fixed bottom-4 right-4 z-50",
          "bg-white rounded-lg shadow-xl p-4 pr-12",
          "border border-neutral-200",
          "max-w-sm",
          className
        )}
      >
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <Info className="w-5 h-5 text-primary-600" />
          </div>
          <p className="text-sm text-neutral-700">{message}</p>
        </div>
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </motion.div>
    </AnimatePresence>
  );
}