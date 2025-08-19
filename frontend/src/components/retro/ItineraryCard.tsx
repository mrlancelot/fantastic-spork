import React from 'react';
import { Plane, Home, Utensils, MapPin } from 'lucide-react';
import { theme } from './index';

interface ItineraryCardProps {
  type: 'flight' | 'hotel' | 'meal' | 'activity';
  title: string;
  subtitle: string;
  time?: string;
  location?: string;
}

export const ItineraryCard: React.FC<ItineraryCardProps> = ({ type, title, subtitle, time, location }) => {
  const typeConfig = {
    flight: { icon: <Plane className="w-5 h-5" />, color: theme.colors.blue },
    hotel: { icon: <Home className="w-5 h-5" />, color: theme.colors.green },
    meal: { icon: <Utensils className="w-5 h-5" />, color: theme.colors.orange },
    activity: { icon: <MapPin className="w-5 h-5" />, color: 'bg-purple-400 text-white' }
  };

  const config = typeConfig[type] || typeConfig.activity;

  return (
    <div className="bg-white border-2 border-[#222222] rounded-[10px] p-3 shadow-[0_2px_0_0_#222222]">
      <div className="flex items-start gap-3">
        <div className={`${config.color} p-2 rounded-[8px] border border-[#222222]`}>
          {config.icon}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">{title}</h3>
          <p className="text-sm text-[#4E4E4E]">{subtitle}</p>
          <div className="flex gap-4 mt-1 text-xs text-[#4E4E4E]">
            {time && <span>{time}</span>}
            {location && <span>{location}</span>}
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full border border-[#222222] ${config.color}`}>
          {type.toUpperCase()}
        </span>
      </div>
    </div>
  );
};