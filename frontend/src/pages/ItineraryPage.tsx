import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MessageSquare, Send } from 'lucide-react';
import { Button, Input, theme } from '../components/retro';
import { ItineraryCard } from '../components/retro/ItineraryCard';
import { DayTabs } from '../components/retro/DayTabs';
import { ItineraryResponse, Activity } from '../services/api';
import { ItineraryHeader } from '../components/ItineraryHeader';
import { ResizableChat } from '../components/ResizableChat';

export const ItineraryPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [assistantInput, setAssistantInput] = useState('');
  const [activeDay, setActiveDay] = useState(1);

  // Get itinerary data from navigation state
  const { itineraryData, formData } = location.state as {
    itineraryData: ItineraryResponse;
    formData: any;
  } || {};

  // Redirect to home if no data
  if (!itineraryData) {
    navigate('/');
    return null;
  }

  // Helper function to format date
  const formatDate = (dayNumber: number, startDate?: string) => {
    const dayData = itineraryData.days.find(d => d.day_number === dayNumber);
    if (dayData) {
      return `${dayData.date}, ${dayData.year}`;
    }

    // Fallback logic if day data doesn't have date
    if (!startDate) {
      const today = new Date();
      const targetDate = new Date(today);
      targetDate.setDate(today.getDate() + (dayNumber - 1));
      
      return targetDate.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
    
    const start = new Date(startDate);
    const targetDate = new Date(start);
    targetDate.setDate(start.getDate() + (dayNumber - 1));
    
    return targetDate.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Convert API activity to ItineraryCard props
  const convertActivityToCard = (activity: Activity) => {
    return {
      type: activity.activity_type,
      title: activity.title,
      subtitle: activity.description,
      time: activity.time,
      location: activity.location
    };
  };

  const totalDays = itineraryData.total_days;
  const currentDayData = itineraryData.days.find(day => day.day_number === activeDay);
  
  const suggestions = [
    'Add more time at museums',
    'Find vegetarian restaurants', 
    'Add nightlife activities',
    'Change hotel location'
  ];

  // Prepare trip details for header
  const tripDetails = {
    from: formData?.from || 'SFO',
    to: formData?.to || 'NRT', 
    departureDate: formData?.departureDate || '2025-08-24',
    returnDate: formData?.returnDate,
    passengers: formData?.passengers || 1,
    travelClass: formData?.travelClass || 'economy'
  };

  const handleBackToSearch = () => {
    navigate('/');
  };

  const handleSaveTrip = () => {
    // TODO: Implement save trip functionality
    console.log('Save trip clicked');
  };

  const handleMyTrips = () => {
    navigate('/my-trips');
  };

  const handleSignIn = () => {
    // TODO: Implement sign in functionality
    console.log('Sign in clicked');
  };

  return (
    <div className={`h-screen ${theme.colors.canvas} flex flex-col overflow-hidden`}>
      {/* Header */}
      <ItineraryHeader
        tripDetails={tripDetails}
        onBackToSearch={handleBackToSearch}
        onSaveTrip={handleSaveTrip}
        onMyTrips={handleMyTrips}
        onSignIn={handleSignIn}
      />
      
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {/* Day Tabs - aligned with cards */}
            <div className="ml-16">
              <DayTabs 
                days={totalDays} 
                activeDay={activeDay} 
                onDayChange={setActiveDay} 
              />
            </div>

            {/* Current Day Content */}
            {currentDayData && (
              <div>
                {/* Date Header */}
                <div className="text-center mb-8">
                  <h2 className="text-xl font-bold">{formatDate(activeDay)}</h2>
                  <p className="text-gray-500 text-sm">{currentDayData.year}</p>
                </div>

                {/* Day Items */}
                <div className="space-y-3">
                  {currentDayData.activities.map((activity, itemIndex) => (
                    <div key={itemIndex} className="flex items-start gap-4">
                      <div className="text-sm text-gray-500 w-12 pt-3">
                        {activity.time}
                      </div>
                      <div className="flex-1">
                        <ItineraryCard {...convertActivityToCard(activity)} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Travel Assistant - Resizable */}
        <div className="pt-8 pr-4 pb-4">
          <ResizableChat minWidth={300} maxWidth={600} defaultWidth={320}>
              <div className="w-full h-full bg-[#E8E3F3] border-2 border-[#222222] rounded-[12px] shadow-[0_4px_0_0_#222222] flex flex-col">
                {/* Header */}
                <div className="bg-[#B794F6] border-b-2 border-[#222222] px-4 py-3 rounded-t-[10px] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-white" />
                <span className="text-white font-bold text-sm">Travel Assistant</span>
              </div>
              <div className="flex gap-1">
                <div className="w-3 h-3 bg-[#FFD700] border border-[#222222] rounded-sm"></div>
                <div className="w-3 h-3 bg-[#32CD32] border border-[#222222] rounded-sm"></div>
              </div>
            </div>
            
            {/* Content */}
            <div className="flex-1 flex flex-col">
              {/* Chat area - scrollable */}
              <div className="flex-1 p-4 space-y-4 overflow-y-auto">
                <div className="bg-purple-50 border-2 border-[#222222] rounded-[10px] p-3">
                  <p className="text-sm">
                    Hi! I've created your itinerary for {formData?.to || itineraryData.trip_details?.route}. 
                    I can help modify your itinerary. What would you like to change?
                  </p>
                </div>
                
                <div className="space-y-2">
                  {suggestions.map((suggestion, i) => (
                    <Button key={i} variant="secondary" className="w-full text-left text-sm">
                      {suggestion}
                    </Button>
                  ))}
                </div>
              </div>
              
              {/* Input bar - pinned to bottom */}
              <div className="border-t-2 border-[#ECE7DF] p-4">
                <div className="flex gap-2 w-full">
                  <div className="flex-1">
                    <Input
                      value={assistantInput}
                      onChange={(e) => setAssistantInput(e.target.value)}
                      placeholder="Ask me to modify your itinerary..."
                      className=""
                    />
                  </div>
                  <Button variant="primary" className="flex-shrink-0">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
          </ResizableChat>
        </div>
      </div>
    </div>
  );
};