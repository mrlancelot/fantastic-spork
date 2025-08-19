import React, { useState } from 'react';
import { MessageSquare, Send, Plane, Home, Utensils, MapPin } from 'lucide-react';
import { RetroWindow, Button, Input, theme } from '../components/retro';
import { ItineraryCard } from '../components/retro/ItineraryCard';

export const ItineraryPage: React.FC = () => {
  const [assistantInput, setAssistantInput] = useState('');
  
  const itinerary = [
    { day: 'Day 1 - Arrival', items: [
      { type: 'flight' as const, title: 'Flight JL006', subtitle: 'JFK → NRT', time: '11:00 AM', location: 'Terminal 1' },
      { type: 'hotel' as const, title: 'Park Hyatt Tokyo Check-in', subtitle: '5-star luxury hotel', time: '3:00 PM', location: 'Shinjuku' },
      { type: 'meal' as const, title: 'Welcome Dinner at Kozue', subtitle: 'Traditional kaiseki cuisine', time: '7:00 PM', location: 'Hotel 40F' }
    ]},
    { day: 'Day 2 - Exploration', items: [
      { type: 'activity' as const, title: 'Senso-ji Temple Visit', subtitle: 'Historic Buddhist temple', time: '9:00 AM', location: 'Asakusa' },
      { type: 'meal' as const, title: 'Lunch at Tsukiji Market', subtitle: 'Fresh sushi experience', time: '12:30 PM', location: 'Tsukiji' },
      { type: 'activity' as const, title: 'TeamLab Borderless', subtitle: 'Digital art museum', time: '3:00 PM', location: 'Odaiba' }
    ]}
  ];

  const suggestions = [
    'Add more time at museums',
    'Find vegetarian restaurants',
    'Add nightlife activities',
    'Change hotel location'
  ];

  return (
    <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
      <div className="max-w-6xl mx-auto">
        <div className="flex gap-4">
          <div className="flex-1 space-y-4">
            {itinerary.map((day, dayIndex) => (
              <div key={dayIndex}>
                <h2 className="font-bold text-lg mb-3 px-2">{day.day}</h2>
                <div className="space-y-2">
                  {day.items.map((item, itemIndex) => (
                    <ItineraryCard key={itemIndex} {...item} />
                  ))}
                </div>
              </div>
            ))}
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