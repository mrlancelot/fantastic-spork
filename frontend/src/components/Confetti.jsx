import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Confetti = ({ duration = 3000 }) => {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    // Generate confetti particles
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * window.innerWidth,
      y: -50,
      rotation: Math.random() * 360,
      color: ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][Math.floor(Math.random() * 6)],
      size: Math.random() * 10 + 5,
      velocity: {
        x: (Math.random() - 0.5) * 4,
        y: Math.random() * 3 + 2
      },
      angularVelocity: (Math.random() - 0.5) * 10
    }));

    setParticles(newParticles);

    const timer = setTimeout(() => {
      setParticles([]);
    }, duration);

    return () => clearTimeout(timer);
  }, [duration]);

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      <AnimatePresence>
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            initial={{
              x: particle.x,
              y: particle.y,
              rotate: particle.rotation,
              opacity: 1
            }}
            animate={{
              y: window.innerHeight + 100,
              x: particle.x + particle.velocity.x * 50,
              rotate: particle.rotation + particle.angularVelocity * 50,
              opacity: 0
            }}
            transition={{
              duration: 3,
              ease: "easeOut"
            }}
            exit={{ opacity: 0 }}
            className="absolute"
            style={{
              width: particle.size,
              height: particle.size,
              backgroundColor: particle.color,
              borderRadius: Math.random() > 0.5 ? '50%' : '0%'
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

export default Confetti;