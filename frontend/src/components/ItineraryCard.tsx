import React from 'react';
import { Clock, MapPin, DollarSign } from 'lucide-react';
import { ItineraryDay } from '../types';
import { formatDateShort, formatTime } from '../utils/dateUtils';

interface ItineraryCardProps {
  day: ItineraryDay;
  dayNumber: number;
}

export const ItineraryCard: React.FC<ItineraryCardProps> = ({ day, dayNumber }) => {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'sightseeing':
        return '🏛️';
      case 'restaurant':
        return '🍽️';
      case 'hotel':
        return '🏨';
      case 'transport':
        return '✈️';
      case 'activity':
        return '🎯';
      default:
        return '📍';
    }
  };

  const totalCost = day.activities.reduce((sum, activity) => sum + (activity.cost || 0), 0);

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            Day {dayNumber}
          </h3>
          <p className="text-gray-600">{formatDateShort(day.date)}</p>
        </div>
        {totalCost > 0 && (
          <div className="flex items-center text-green-600">
            <DollarSign className="h-4 w-4" />
            <span className="font-medium">${totalCost}</span>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {day.activities.map((activity) => (
          <div key={activity.id} className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-lg">{getActivityIcon(activity.type)}</span>
              </div>
            </div>
            
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-600">
                      {formatTime(activity.time)}
                    </span>
                    <span className="text-sm text-gray-400">•</span>
                    <span className="text-sm text-gray-500">{activity.duration}</span>
                  </div>
                  
                  <h4 className="font-semibold text-gray-900 mb-1">
                    {activity.title}
                  </h4>
                  
                  <p className="text-gray-600 text-sm mb-2">
                    {activity.description}
                  </p>
                  
                  <div className="flex items-center text-gray-500 text-sm">
                    <MapPin className="h-4 w-4 mr-1" />
                    <span>{activity.location}</span>
                  </div>
                </div>
                
                {activity.cost && (
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-900">
                      ${activity.cost}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};