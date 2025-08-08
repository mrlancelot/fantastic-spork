import { createContext, useContext, useState, useEffect } from 'react';

const ConfettiContext = createContext();

export function ConfettiProvider({ children }) {
  const [confettiEnabled, setConfettiEnabled] = useState(() => {
    const saved = localStorage.getItem('confettiEnabled');
    return saved !== null ? JSON.parse(saved) : false; // Default to OFF
  });

  const toggleConfetti = () => {
    setConfettiEnabled(prev => {
      const newValue = !prev;
      localStorage.setItem('confettiEnabled', JSON.stringify(newValue));
      return newValue;
    });
  };

  useEffect(() => {
    localStorage.setItem('confettiEnabled', JSON.stringify(confettiEnabled));
  }, [confettiEnabled]);

  return (
    <ConfettiContext.Provider value={{ confettiEnabled, toggleConfetti }}>
      {children}
    </ConfettiContext.Provider>
  );
}

export function useConfetti() {
  const context = useContext(ConfettiContext);
  if (!context) {
    throw new Error('useConfetti must be used within ConfettiProvider');
  }
  return context;
}