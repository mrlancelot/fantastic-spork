import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MessageSquare, Send } from 'lucide-react';
import { RetroWindow, Button, Input, theme, ResizablePanel } from '../components/retro';
import { ItineraryCard } from '../components/retro/ItineraryCard';
import { DayTabs } from '../components/retro/DayTabs';
import { ItineraryResponse, Activity } from '../services/api';

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

  return (
    <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">{itineraryData.title}</h1>
          <p className="text-gray-600">{itineraryData.personalization}</p>
        </div>

        {/* Day Tabs */}
        <DayTabs 
          days={totalDays} 
          activeDay={activeDay} 
          onDayChange={setActiveDay} 
        />

        <div className="flex gap-4">
          <div className="flex-1">
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
          
          <ResizablePanel 
            defaultWidthPercent={35}
            minWidthPercent={30}
            maxWidthPercent={60}
            storageKey="itinerary-assistant-width"
          >
            <RetroWindow variant="assistant" title="Travel Assistant" icon={<MessageSquare className="w-4 h-4" />}>
              <div className="space-y-4">
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
                
                <div className="border-t-2 border-[#ECE7DF] pt-4">
                  <div className="flex gap-2">
                    <Input
                      value={assistantInput}
                      onChange={(e) => setAssistantInput(e.target.value)}
                      placeholder="Ask me to modify your itinerary..."
                      className="flex-1"
                    />
                    <Button variant="primary">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </RetroWindow>
          </ResizablePanel>
        </div>
      </div>
    </div>
  );
};