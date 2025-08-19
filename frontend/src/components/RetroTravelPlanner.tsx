import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, X, Minus, Square, Plane, Home, Utensils, MapPin, MessageSquare, Send, Calendar, Users, Loader2 } from 'lucide-react';

// Design tokens as Tailwind classes
const theme = {
  colors: {
    canvas: 'bg-[#F9F4ED]',
    surface: 'bg-white',
    ink: 'text-[#222222] border-[#222222]',
    inkWeak: 'text-[#4E4E4E]',
    blue: 'bg-[#4A90E2] text-white',
    green: 'bg-[#6FCF97] text-white',
    orange: 'bg-[#F5A25D] text-white',
    yellow: 'bg-[#F5D547] text-black',
    red: 'bg-[#E94F37] text-white',
    muted: 'bg-[#ECE7DF] border-[#ECE7DF]',
  }
};

// Core Components
const RetroWindow = ({ variant = 'default', title, icon, children, onClose, className = '' }) => {
  const variantStyles = {
    default: 'bg-gray-400',
    flight: theme.colors.blue,
    hotel: theme.colors.green,
    meal: theme.colors.orange,
    error: theme.colors.red,
    assistant: 'bg-purple-400 text-white'
  };

  return (
    <div className={`${theme.colors.surface} border-2 ${theme.colors.ink} rounded-[10px] shadow-[0_4px_0_0_#222222] ${className}`}>
      <div className={`${variantStyles[variant]} px-3 py-2 rounded-t-[8px] flex items-center justify-between border-b-2 border-[#222222]`}>
        <div className="flex items-center gap-2">
          {icon && <span className="w-4 h-4">{icon}</span>}
          <span className="font-semibold text-sm">{title}</span>
        </div>
        <div className="flex gap-1">
          <button className="w-5 h-5 bg-yellow-400 border border-black rounded-sm flex items-center justify-center hover:bg-yellow-500">
            <Minus className="w-3 h-3" />
          </button>
          <button className="w-5 h-5 bg-green-400 border border-black rounded-sm flex items-center justify-center hover:bg-green-500">
            <Square className="w-2 h-2" />
          </button>
          <button onClick={onClose} className="w-5 h-5 bg-red-400 border border-black rounded-sm flex items-center justify-center hover:bg-red-500">
            <X className="w-3 h-3" />
          </button>
        </div>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
};

const Button = ({ variant = 'primary', children, onClick, disabled, className = '' }) => {
  const variants = {
    primary: `${theme.colors.blue} border-2 border-[#222222] shadow-[0_2px_0_0_#222222] hover:shadow-[0_1px_0_0_#222222] hover:translate-y-[1px]`,
    secondary: `${theme.colors.surface} ${theme.colors.ink} border-2 border-[#222222] shadow-[0_2px_0_0_#222222] hover:shadow-[0_1px_0_0_#222222] hover:translate-y-[1px]`,
    ghost: 'hover:bg-gray-100'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-[8px] font-medium transition-all duration-120 disabled:opacity-50 ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

const Input = ({ label, value, onChange, placeholder, type = 'text', className = '' }) => (
  <div className="space-y-1">
    {label && <label className="text-sm font-medium">{label}</label>}
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`w-full px-3 py-2 border-2 border-[#222222] rounded-[8px] bg-white shadow-inner focus:outline-none focus:ring-2 focus:ring-[#4A90E280] ${className}`}
    />
  </div>
);

const Select = ({ label, value, onChange, options, className = '' }) => (
  <div className="space-y-1">
    {label && <label className="text-sm font-medium">{label}</label>}
    <select
      value={value}
      onChange={onChange}
      className={`w-full px-3 py-2 border-2 border-[#222222] rounded-[8px] bg-white shadow-inner focus:outline-none focus:ring-2 focus:ring-[#4A90E280] ${className}`}
    >
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </div>
);

const Tag = ({ selected, children, onClick }) => (
  <button
    onClick={onClick}
    className={`px-3 py-1 rounded-full border-2 border-[#222222] text-sm font-medium transition-all ${
      selected ? 'bg-[#4A90E2] text-white' : 'bg-white hover:bg-gray-50'
    }`}
  >
    {children}
  </button>
);

const ProgressBar = ({ progress }) => {
  const segments = 12;
  const filled = Math.floor((progress / 100) * segments);
  
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-white border-2 border-[#222222] rounded-[8px] p-2">
        <div className="flex gap-1">
          {[...Array(segments)].map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-4 rounded-sm transition-all duration-[60ms] ${
                i < filled ? 'bg-[#4A90E2]' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>
      <span className="font-mono text-sm font-bold">{progress}%</span>
    </div>
  );
};

const ItineraryCard = ({ type, title, subtitle, time, location }) => {
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

// Screen Components
const TripFormScreen = ({ onNext }) => {
  const [formData, setFormData] = useState({
    tripType: 'round',
    from: '',
    to: '',
    departure: '',
    return: '',
    passengers: '1',
    class: 'economy',
    interests: []
  });

  const interests = ['Food tours', 'Museums', 'Outdoor activities', 'Nightlife', 'Shopping', 'Historical sites', 'Local culture', 'Art galleries'];

  const toggleInterest = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  return (
    <RetroWindow variant="default" title="Create Itinerary" icon={<Plane className="w-4 h-4" />}>
      <div className="space-y-6">
        <div className="flex gap-2 p-1 bg-gray-100 rounded-[8px] border-2 border-[#222222]">
          <button
            onClick={() => setFormData(prev => ({ ...prev, tripType: 'round' }))}
            className={`flex-1 py-2 px-3 rounded-[6px] font-medium transition-all ${
              formData.tripType === 'round' ? 'bg-[#4A90E2] text-white' : ''
            }`}
          >
            ROUND TRIP
          </button>
          <button
            onClick={() => setFormData(prev => ({ ...prev, tripType: 'one' }))}
            className={`flex-1 py-2 px-3 rounded-[6px] font-medium transition-all ${
              formData.tripType === 'one' ? 'bg-[#4A90E2] text-white' : ''
            }`}
          >
            ONE WAY
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 flex gap-2 items-end">
            <div className="flex-1">
              <Input
                label="From"
                value={formData.from}
                onChange={(e) => setFormData(prev => ({ ...prev, from: e.target.value }))}
                placeholder="New York"
              />
            </div>
            <Button variant="secondary" className="mb-0">
              <ChevronLeft className="w-4 h-4 inline mr-1" />
              <ChevronRight className="w-4 h-4 inline" />
            </Button>
            <div className="flex-1">
              <Input
                label="To"
                value={formData.to}
                onChange={(e) => setFormData(prev => ({ ...prev, to: e.target.value }))}
                placeholder="Tokyo"
              />
            </div>
          </div>

          <Input
            label="Departure"
            type="date"
            value={formData.departure}
            onChange={(e) => setFormData(prev => ({ ...prev, departure: e.target.value }))}
          />
          
          {formData.tripType === 'round' && (
            <Input
              label="Return"
              type="date"
              value={formData.return}
              onChange={(e) => setFormData(prev => ({ ...prev, return: e.target.value }))}
            />
          )}

          <Select
            label="Passengers"
            value={formData.passengers}
            onChange={(e) => setFormData(prev => ({ ...prev, passengers: e.target.value }))}
            options={[
              { value: '1', label: '1 Passenger' },
              { value: '2', label: '2 Passengers' },
              { value: '3', label: '3 Passengers' },
              { value: '4+', label: '4+ Passengers' }
            ]}
          />

          <Select
            label="Class"
            value={formData.class}
            onChange={(e) => setFormData(prev => ({ ...prev, class: e.target.value }))}
            options={[
              { value: 'economy', label: 'Economy' },
              { value: 'premium', label: 'Premium Economy' },
              { value: 'business', label: 'Business' },
              { value: 'first', label: 'First' }
            ]}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">What interests you?</label>
          <div className="flex flex-wrap gap-2">
            {interests.map(interest => (
              <Tag
                key={interest}
                selected={formData.interests.includes(interest)}
                onClick={() => toggleInterest(interest)}
              >
                {interest}
              </Tag>
            ))}
          </div>
        </div>

        <Button onClick={onNext} className="w-full">
          Create itinerary →
        </Button>
      </div>
    </RetroWindow>
  );
};

const LoadingScreen = ({ onNext }) => {
  const [progress, setProgress] = useState(0);
  const [tasks, setTasks] = useState([
    { name: 'Flights', status: 'loading', detail: 'Searching best flight deals...' },
    { name: 'Hotels', status: 'pending', detail: 'Ready to search' },
    { name: 'Restaurants', status: 'pending', detail: 'Ready to search' },
    { name: 'Attractions', status: 'pending', detail: 'Ready to search' }
  ]);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(onNext, 500);
          return 100;
        }
        return prev + 5;
      });
    }, 180);

    const taskInterval = setInterval(() => {
      setTasks(prev => {
        const loading = prev.findIndex(t => t.status === 'loading');
        if (loading === -1) return prev;
        
        const newTasks = [...prev];
        if (loading < prev.length) {
          newTasks[loading].status = 'done';
          newTasks[loading].detail = `Found ${Math.floor(Math.random() * 20) + 5} options!`;
          
          if (loading + 1 < prev.length) {
            newTasks[loading + 1].status = 'loading';
            newTasks[loading + 1].detail = `Searching best ${newTasks[loading + 1].name.toLowerCase()} options...`;
          }
        }
        return newTasks;
      });
    }, 1500);

    return () => {
      clearInterval(interval);
      clearInterval(taskInterval);
    };
  }, [onNext]);

  return (
    <RetroWindow variant="default" title="Creating your itinerary" icon={<Loader2 className="w-4 h-4 animate-spin" />}>
      <div className="space-y-6">
        <ProgressBar progress={progress} />
        
        <div className="space-y-3">
          {tasks.map((task, i) => (
            <div key={i} className="bg-white border-2 border-[#222222] rounded-[10px] p-3">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-[8px] border border-[#222222] flex items-center justify-center ${
                  task.status === 'done' ? 'bg-green-400' : 
                  task.status === 'loading' ? 'bg-yellow-400' : 
                  'bg-gray-200'
                }`}>
                  {task.status === 'done' ? '✓' : 
                   task.status === 'loading' ? '...' : 
                   ''}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-sm">{task.name}</div>
                  <div className="text-xs text-[#4E4E4E]">{task.detail}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center text-sm text-[#4E4E4E] border-t-2 border-[#ECE7DF] pt-3">
          This may take a few moments...
        </div>
      </div>
    </RetroWindow>
  );
};

const ItineraryScreen = () => {
  const [assistantInput, setAssistantInput] = useState('');
  
  const itinerary = [
    { day: 'Day 1 - Arrival', items: [
      { type: 'flight', title: 'Flight JL006', subtitle: 'JFK → NRT', time: '11:00 AM', location: 'Terminal 1' },
      { type: 'hotel', title: 'Park Hyatt Tokyo Check-in', subtitle: '5-star luxury hotel', time: '3:00 PM', location: 'Shinjuku' },
      { type: 'meal', title: 'Welcome Dinner at Kozue', subtitle: 'Traditional kaiseki cuisine', time: '7:00 PM', location: 'Hotel 40F' }
    ]},
    { day: 'Day 2 - Exploration', items: [
      { type: 'activity', title: 'Senso-ji Temple Visit', subtitle: 'Historic Buddhist temple', time: '9:00 AM', location: 'Asakusa' },
      { type: 'meal', title: 'Lunch at Tsukiji Market', subtitle: 'Fresh sushi experience', time: '12:30 PM', location: 'Tsukiji' },
      { type: 'activity', title: 'TeamLab Borderless', subtitle: 'Digital art museum', time: '3:00 PM', location: 'Odaiba' }
    ]}
  ];

  const suggestions = [
    'Add more time at museums',
    'Find vegetarian restaurants',
    'Add nightlife activities',
    'Change hotel location'
  ];

  return (
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
  );
};

// Main App
export default function RetroTravelPlanner() {
  const [currentScreen, setCurrentScreen] = useState('form');

  return (
    <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
      <div className="max-w-6xl mx-auto">
        {currentScreen === 'form' && (
          <TripFormScreen onNext={() => setCurrentScreen('loading')} />
        )}
        {currentScreen === 'loading' && (
          <LoadingScreen onNext={() => setCurrentScreen('itinerary')} />
        )}
        {currentScreen === 'itinerary' && (
          <ItineraryScreen />
        )}
      </div>
    </div>
  );
}