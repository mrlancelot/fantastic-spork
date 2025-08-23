import React from 'react';
import { theme } from './index';

interface DayTabsProps {
  days: number;
  activeDay: number;
  onDayChange: (day: number) => void;
}

export const DayTabs: React.FC<DayTabsProps> = ({ days, activeDay, onDayChange }) => {
  return (
    <div className="flex gap-1 mb-6">
      {Array.from({ length: days }, (_, index) => {
        const dayNumber = index + 1;
        const isActive = activeDay === dayNumber;
        
        return (
          <button
            key={dayNumber}
            onClick={() => onDayChange(dayNumber)}
            className={`px-4 py-2 rounded-[8px] border-2 border-[#222222] font-medium transition-all ${
              isActive 
                ? 'bg-[#4A90E2] text-white shadow-[0_2px_0_0_#222222]' 
                : 'bg-white text-[#222222] hover:bg-gray-50'
            }`}
          >
            Day {dayNumber}
          </button>
        );
      })}
    </div>
  );
};
