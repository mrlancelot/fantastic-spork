import { motion } from 'framer-motion';
import { Button } from './Button';
import { cn } from '../../utils/cn';

const FloatingElement = ({ delay = 0, duration = 20, children, className }) => (
  <motion.div
    className={cn("absolute", className)}
    animate={{
      y: [0, -20, 0],
      x: [0, 10, -10, 0],
      rotate: [0, 5, -5, 0],
    }}
    transition={{
      duration,
      repeat: Infinity,
      delay,
      ease: "easeInOut",
    }}
  >
    {children}
  </motion.div>
);

export function HeroSection({ title, subtitle, ctaText, onCtaClick, className }) {
  return (
    <div className={cn("relative overflow-hidden", className)}>
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-secondary-50 to-accent-50 animate-gradient" />
      
      {/* Floating decorative elements */}
      <FloatingElement delay={0} duration={15} className="top-20 left-10 w-64 h-64">
        <div className="w-full h-full rounded-full bg-gradient-to-br from-primary-400/20 to-primary-600/20 blur-3xl" />
      </FloatingElement>
      
      <FloatingElement delay={5} duration={20} className="bottom-20 right-10 w-96 h-96">
        <div className="w-full h-full rounded-full bg-gradient-to-br from-secondary-400/20 to-secondary-600/20 blur-3xl" />
      </FloatingElement>
      
      <FloatingElement delay={10} duration={25} className="top-40 right-40 w-72 h-72">
        <div className="w-full h-full rounded-full bg-gradient-to-br from-accent-400/20 to-accent-600/20 blur-3xl" />
      </FloatingElement>
      
      {/* Glass morphism cards floating */}
      <FloatingElement delay={2} duration={18} className="top-32 right-20">
        <div className="glass rounded-lg p-4 shadow-xl">
          <div className="w-32 h-20 bg-gradient-to-br from-primary-400 to-primary-600 rounded" />
        </div>
      </FloatingElement>
      
      <FloatingElement delay={7} duration={22} className="bottom-32 left-20">
        <div className="glass rounded-lg p-4 shadow-xl">
          <div className="w-40 h-24 bg-gradient-to-br from-secondary-400 to-secondary-600 rounded" />
        </div>
      </FloatingElement>
      
      {/* Main content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <motion.h1 
            className="text-5xl md:text-7xl font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <span className="gradient-text">{title}</span>
          </motion.h1>
          
          <motion.p 
            className="text-xl md:text-2xl text-neutral-600 mb-8 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {subtitle}
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            whileHover={{ scale: 1.05 }}
          >
            <Button
              size="xl"
              variant="gradient"
              onClick={onCtaClick}
              className="shadow-2xl hover:shadow-primary-500/25"
            >
              {ctaText}
            </Button>
          </motion.div>
        </motion.div>
        
        {/* Animated scroll indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-6 h-10 border-2 border-neutral-400 rounded-full p-1">
            <div className="w-1 h-3 bg-neutral-400 rounded-full mx-auto animate-pulse" />
          </div>
        </motion.div>
      </div>
    </div>
  );
}