import React from 'react';
import { ArrowLeft, MapPin, Bookmark, User } from 'lucide-react';
import { theme } from './retro';

interface ItineraryHeaderProps {
  tripDetails?: {
    from: string;
    to: string;
    departureDate: string;
    returnDate?: string;
    passengers: number;
    travelClass: string;
  };
  onBackToSearch?: () => void;
  onSaveTrip?: () => void;
  onMyTrips?: () => void;
  onSignIn?: () => void;
}

export const ItineraryHeader: React.FC<ItineraryHeaderProps> = ({
  tripDetails,
  onBackToSearch,
  onSaveTrip,
  onMyTrips,
  onSignIn
}) => {
  const formatTripDetails = () => {
    if (!tripDetails) return '';
    
    const { from, to, departureDate, returnDate, passengers, travelClass } = tripDetails;
    
    // Format dates
    const formatDate = (dateStr: string) => {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };
    
    const dateRange = returnDate 
      ? `${formatDate(departureDate)} - ${formatDate(returnDate)}`
      : formatDate(departureDate);
    
    const passengerText = passengers === 1 ? '1 traveler' : `${passengers} travelers`;
    const classText = travelClass.charAt(0).toUpperCase() + travelClass.slice(1);
    
    return `${from} → ${to}, ${dateRange} • ${passengerText} • ${classText}`;
  };

  return (
    <header className={`${theme.colors.canvas} px-6 py-4`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left section - Back button */}
        <div className="flex items-center">
          <button
            onClick={onBackToSearch}
            className="flex items-center gap-2 text-[#4E4E4E] hover:text-[#222222] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Back to search</span>
          </button>
        </div>

        {/* Center section - Logo and trip details */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#4A90E2] rounded-full border-2 border-[#222222] flex items-center justify-center">
              <MapPin className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-bold text-[#222222]">Waypoint</span>
          </div>
          
          {tripDetails && (
            <div className="text-sm text-[#4E4E4E] ml-4">
              {formatTripDetails()}
            </div>
          )}
        </div>

        {/* Right section - Action buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={onSaveTrip}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-[#4E4E4E] hover:text-[#222222] hover:bg-gray-50 rounded-[6px] transition-colors"
          >
            <Bookmark className="w-4 h-4" />
            Save trip
          </button>
          
          <button
            onClick={() => {
              if (onMyTrips) {
                onMyTrips();
              } else {
                window.location.href = '/my-trips';
              }
            }}
            className="px-3 py-2 text-sm font-medium text-[#4E4E4E] hover:text-[#222222] hover:bg-gray-50 rounded-[6px] transition-colors"
          >
            My trips
          </button>
          
          <button
            onClick={onSignIn}
            className="flex items-center gap-2 px-4 py-2 bg-[#4A90E2] text-white text-sm font-medium rounded-[8px] border-2 border-[#222222] shadow-[0_2px_0_0_#222222] hover:shadow-[0_1px_0_0_#222222] hover:translate-y-[1px] transition-all"
          >
            <User className="w-4 h-4" />
            Sign in
          </button>
        </div>
      </div>
    </header>
  );
};
