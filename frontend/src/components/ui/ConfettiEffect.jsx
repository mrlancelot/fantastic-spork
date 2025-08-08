import { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { useConfetti } from '../../contexts/ConfettiContext';

export default function ConfettiEffect({ show, duration = 3000 }) {
  const { confettiEnabled } = useConfetti();
  
  useEffect(() => {
    if (!show || !confettiEnabled) return;

    const runConfetti = () => {
      // Burst from center
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });

      // Side bursts
      setTimeout(() => {
        confetti({
          particleCount: 50,
          angle: 60,
          spread: 55,
          origin: { x: 0 }
        });
        confetti({
          particleCount: 50,
          angle: 120,
          spread: 55,
          origin: { x: 1 }
        });
      }, 300);

      // Continuous small bursts
      const interval = setInterval(() => {
        confetti({
          particleCount: 30,
          spread: 60,
          origin: { 
            y: Math.random() * 0.4 + 0.3,
            x: Math.random() * 0.6 + 0.2
          }
        });
      }, 500);

      setTimeout(() => {
        clearInterval(interval);
      }, duration - 500);
    };

    runConfetti();
  }, [show, duration]);

  return null;
}