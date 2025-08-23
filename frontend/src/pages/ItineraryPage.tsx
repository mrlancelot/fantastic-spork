import React, { useState } from 'react';
import { MessageSquare, Send } from 'lucide-react';
import { RetroWindow, Button, Input, theme } from '../components/retro';
import { ItineraryCard } from '../components/retro/ItineraryCard';
import { DayTabs } from '../components/retro/DayTabs';

export const ItineraryPage: React.FC = () => {
  const [assistantInput, setAssistantInput] = useState('');
  const [activeDay, setActiveDay] = useState(1);
  
  // Helper function to format date
  const formatDate = (dayNumber: number, startDate?: string) => {
    if (!startDate) {
      // Fallback to current date if no start date provided
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
  
  const itinerary = [
    { day: 1, title: 'Arrival', items: [
      { type: 'flight' as const, title: 'Flight JL006', subtitle: 'JFK → NRT', time: '11:00 AM', location: 'Terminal 1' },
      { type: 'hotel' as const, title: 'Park Hyatt Tokyo Check-in', subtitle: '5-star luxury hotel', time: '3:00 PM', location: 'Shinjuku' },
      { type: 'meal' as const, title: 'Welcome Dinner at Kozue', subtitle: 'Traditional kaiseki cuisine', time: '7:00 PM', location: 'Hotel 40F' }
    ]},
    { day: 2, title: 'Exploration', items: [
      { type: 'activity' as const, title: 'Senso-ji Temple Visit', subtitle: 'Historic Buddhist temple', time: '9:00 AM', location: 'Asakusa' },
      { type: 'meal' as const, title: 'Lunch at Tsukiji Market', subtitle: 'Fresh sushi experience', time: '12:30 PM', location: 'Tsukiji' },
      { type: 'activity' as const, title: 'TeamLab Borderless', subtitle: 'Digital art museum', time: '3:00 PM', location: 'Odaiba' }
    ]},
    { day: 3, title: 'Cultural Immersion', items: [
      { type: 'activity' as const, title: 'Meiji Shrine Visit', subtitle: 'Peaceful Shinto shrine', time: '9:00 AM', location: 'Shibuya' },
      { type: 'meal' as const, title: 'Ramen Cooking Class', subtitle: 'Learn to make authentic ramen', time: '1:00 PM', location: 'Harajuku' },
      { type: 'activity' as const, title: 'Kabuki Performance', subtitle: 'Traditional Japanese theater', time: '6:00 PM', location: 'Ginza' }
    ]},
    { day: 4, title: 'Departure', items: [
      { type: 'hotel' as const, title: 'Hotel Check-out', subtitle: 'Park Hyatt Tokyo', time: '11:00 AM', location: 'Shinjuku' },
      { type: 'meal' as const, title: 'Farewell Lunch', subtitle: 'Last taste of Tokyo', time: '12:30 PM', location: 'Airport' },
      { type: 'flight' as const, title: 'Flight JL005', subtitle: 'NRT → JFK', time: '3:00 PM', location: 'Terminal 1' }
    ]}
  ];

  const totalDays = itinerary.length;
  const currentDayData = itinerary.find(day => day.day === activeDay);
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
          <h1 className="text-2xl font-bold mb-2">Your Itinerary</h1>
          <p className="text-gray-600">General sightseeing and local experiences</p>
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
                  <p className="text-gray-500 text-sm">{new Date().getFullYear()}</p>
                </div>

                {/* Day Items */}
                <div className="space-y-3">
                  {currentDayData.items.map((item, itemIndex) => (
                    <div key={itemIndex} className="flex items-start gap-4">
                      <div className="text-sm text-gray-500 w-12 pt-3">
                        {item.time}
                      </div>
                      <div className="flex-1">
                        <ItineraryCard {...item} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="w-80">
            <RetroWindow variant="assistant" title="Travel Assistant" icon={<MessageSquare className="w-4 h-4" />}>
              <div className="space-y-4">
                <div className="bg-purple-50 border-2 border-[#222222] rounded-[10px] p-3">
                  <p className="text-sm">
                    Hi! I'm your travel assistant. I can help modify your itinerary. What would you like to change?
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
          </div>
        </div>
      </div>
    </div>
  );
};