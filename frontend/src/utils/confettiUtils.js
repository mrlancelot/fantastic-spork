import confetti from 'canvas-confetti';

export const isConfettiEnabled = () => {
  const saved = localStorage.getItem('confettiEnabled');
  return saved !== null ? JSON.parse(saved) : true;
};

export const triggerConfetti = (options = {}) => {
  if (!isConfettiEnabled()) return;
  
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    ...options
  });
};

export const celebrationConfetti = () => {
  if (!isConfettiEnabled()) return;
  
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 }
  });
  
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
};