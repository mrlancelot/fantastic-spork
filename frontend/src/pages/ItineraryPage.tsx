import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MapPin, 
  ArrowLeft, 
  Clock, 
  Send, 
  Heart, 
  Plane, 
  Building, 
  UtensilsCrossed, 
  GripVertical,
  Bot,
  User,
  X,
  Camera,
  Car,
  Calendar,
  AlertCircle
} from 'lucide-react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useTripContext } from '../context/TripContext';
import { mapActivityType } from '../services/api';

interface ItineraryItem {
  id: string;
  time: string;
  title: string;
  description: string;
  location: string;
  type: 'flight' | 'hotel' | 'meal' | 'activity' | 'transport';
  tag: string;
  duration?: string;
}

interface DayData {
  dayNumber: number;
  date: string;
  year: number;
  items: ItineraryItem[];
  day_name?: string;  // New field from backend
  month_day?: string; // New field from backend
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SortableItineraryCard: React.FC<{ item: ItineraryItem }> = ({ item }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getIcon = () => {
    switch (item.type) {
      case 'flight':
        return <Plane className="w-5 h-5 text-blue-600" />;
      case 'hotel':
        return <Building className="w-5 h-5 text-green-600" />;
      case 'meal':
        return <UtensilsCrossed className="w-5 h-5 text-orange-600" />;
      case 'activity':
        return <Camera className="w-5 h-5 text-purple-600" />;
      case 'transport':
        return <Car className="w-5 h-5 text-gray-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getTagColor = () => {
    switch (item.type) {
      case 'flight':
        return 'bg-blue-100 text-blue-800';
      case 'hotel':
        return 'bg-green-100 text-green-800';
      case 'meal':
        return 'bg-orange-100 text-orange-800';
      case 'activity':
        return 'bg-purple-100 text-purple-800';
      case 'transport':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`bg-white border border-gray-200 rounded-lg p-4 sortable-item group ${
        isDragging ? 'is-dragging' : ''
      } hover:shadow-md`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          <div className="text-sm font-medium text-gray-900 min-w-[60px]">
            {item.time}
          </div>
          <div className="flex items-start space-x-3 flex-1">
            {getIcon()}
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">
                {item.title}
              </h3>
              <p className="text-gray-600 text-sm mb-2 leading-relaxed">
                {item.description}
              </p>
              <div className="space-y-1">
                {item.location && (
                  <p className="text-gray-500 text-sm flex items-center">
                    <MapPin className="w-3 h-3 mr-1" />
                    {item.location}
                  </p>
                )}
                {item.duration && (
                  <p className="text-gray-400 text-xs flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    Duration: {item.duration}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${getTagColor()}`}>
            {item.tag}
          </span>
          <div
            className="opacity-0 group-hover:opacity-100 drag-handle p-1"
            {...attributes}
            {...listeners}
          >
            <GripVertical className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>
    </div>
  );
};

export const ItineraryPage: React.FC = () => {
  const navigate = useNavigate();
  const { formData, itineraryData, clearData } = useTripContext();
  const [chatMessage, setChatMessage] = useState('');
  const [isReordering, setIsReordering] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [selectedDay, setSelectedDay] = useState(0);
  const [days, setDays] = useState<DayData[]>([]);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Initialize data from context
  useEffect(() => {
    if (!itineraryData) {
      // No data, redirect to home
      navigate('/');
      return;
    }

    // Transform backend data to frontend format
    const transformedDays: DayData[] = itineraryData.days.map(day => ({
      dayNumber: day.day_number,
      date: day.date,
      year: day.year,
      day_name: day.day_name,  // Include new field
      month_day: day.month_day, // Include new field
      items: day.activities.map((activity, index) => ({
        id: `day${day.day_number}-${index}`,
        time: activity.time,
        title: activity.title,
        description: activity.description,
        location: activity.location || '',
        type: activity.activity_type as any,
        tag: activity.activity_type.replace('_', ' '),
        duration: activity.duration
      }))
    }));

    setDays(transformedDays);

    // Set initial chat message
    const destination = formData?.destination || 'your destination';
    setMessages([{
      id: '1',
      type: 'assistant',
      content: `Hi! I've created your ${itineraryData.total_days}-day itinerary for ${destination}. ${itineraryData.personalization} You can ask me to modify any part of your trip, add new activities, change restaurants, or adjust timing. What would you like to change?`,
      timestamp: new Date(),
    }]);
  }, [itineraryData, formData, navigate]);

  const handleBack = () => {
    if (window.confirm('Are you sure you want to go back? Your itinerary will be cleared.')) {
      clearData();
      navigate('/');
    }
  };

  const handleSendMessage = () => {
    if (!chatMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: chatMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setChatMessage('');

    // Auto-scroll to bottom
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);

    // Show typing indicator
    setIsTyping(true);
    
    // Simulate AI response
    setTimeout(() => {
      setIsTyping(false);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Thanks for your message! I can help you modify your itinerary. To make real changes, this feature will be connected to the backend API soon. What specific changes would you like me to make?',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Auto-scroll to bottom again
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }, 1500);
  };

  const handleDragStart = () => {
    setIsReordering(true);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setIsReordering(false);

    if (active.id !== over?.id) {
      setDays((prevDays) => {
        const newDays = [...prevDays];
        const currentDay = newDays[selectedDay];
        const oldIndex = currentDay.items.findIndex((item) => item.id === active.id);
        const newIndex = currentDay.items.findIndex((item) => item.id === over?.id);
        
        newDays[selectedDay] = {
          ...currentDay,
          items: arrayMove(currentDay.items, oldIndex, newIndex)
        };

        // Add a brief success message with typing indicator
        setTimeout(() => {
          setIsTyping(true);
          setTimeout(() => {
            setIsTyping(false);
            const successMessage: Message = {
              id: (Date.now() + Math.random()).toString(),
              type: 'assistant',
              content: 'Itinerary reordered successfully! Your changes have been saved.',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, successMessage]);
            
            // Auto-scroll to bottom
            setTimeout(() => {
              messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, 100);
          }, 800);
        }, 300);

        return newDays;
      });
    }
  };

  const examplePrompts = [
    "Add more time at museums",
    "Find vegetarian restaurants", 
    "Add nightlife activities",
    "Change hotel location"
  ];

  // Format dates for display
  const formatDateRange = () => {
    if (!formData) return '';
    
    const start = formData.startDate ? formData.startDate.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    }) : '';
    
    const end = formData.endDate ? formData.endDate.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    }) : formData.startDate ? formData.startDate.toLocaleDateString('en-US', { 
      year: 'numeric'
    }) : '';
    
    return formData.tripType === 'roundtrip' ? `${start} - ${end}` : `${start}, ${end}`;
  };

  const formatDayDate = (dayData: DayData) => {
    // The backend now sends day_name and month_day fields
    // Use them directly if available
    if ('day_name' in dayData && 'month_day' in dayData) {
      return `${(dayData as any).day_name}, ${(dayData as any).month_day}`;
    }
    
    // Fallback: Parse the date string if it's in YYYY-MM-DD format
    if (dayData.date && dayData.date.includes('-')) {
      const dateObj = new Date(dayData.date);
      const weekday = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
      const monthDay = dateObj.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
      return `${weekday}, ${monthDay}`;
    }
    
    // Last fallback: return the date as-is
    return dayData.date;
  };

  if (!itineraryData || days.length === 0) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Itinerary Found</h2>
          <p className="text-gray-600 mb-4">Please create a new itinerary from the search page.</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Search
          </button>
        </div>
      </div>
    );
  }

  const currentDay = days[selectedDay];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-6">
              <button 
                onClick={handleBack}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              
              <div className="flex items-center space-x-2">
                <MapPin className="h-6 w-6 text-blue-600" />
                <span className="text-lg font-semibold text-gray-900">Waypoint</span>
              </div>
              
              <div className="text-gray-900 font-medium">
                {formData?.fromCity} → {formData?.destination}
                <div className="text-sm text-gray-500">
                  {formatDateRange()}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                <Heart className="w-4 h-4" />
                <span>Save trip</span>
              </button>
              <a href="#" className="text-gray-700 hover:text-blue-600 font-medium">My trips</a>
              <a href="#" className="text-gray-700 hover:text-blue-600 font-medium">Sign in</a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Two Panel Layout */}
      <div className="flex h-[calc(100vh-64px)]">
        {/* Left Panel - Itinerary */}
        <div className={`flex-1 overflow-y-auto pt-8 px-8 pb-12 transition-all duration-300 ${
          isChatOpen ? 'flex justify-center' : 'flex justify-center'
        }`}>
          <div className={`transition-all duration-300 w-full px-6 pb-8 ${
            isChatOpen ? 'max-w-2xl' : 'max-w-4xl'
          }`}>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">
              {itineraryData.title}
            </h1>
            <p className="text-gray-600 mb-8">
              {itineraryData.personalization}
            </p>

            {/* Day Selector Tabs */}
            {days.length > 1 && (
              <div className="flex space-x-2 mb-6 border-b border-gray-200">
                {days.map((day, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedDay(index)}
                    className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
                      selectedDay === index
                        ? 'text-blue-600 border-blue-600'
                        : 'text-gray-600 border-transparent hover:text-gray-900'
                    }`}
                  >
                    Day {day.dayNumber}
                  </button>
                ))}
              </div>
            )}

            {/* Current Day */}
            <div className="mb-8">
              <div className="mb-6">
                <div className="text-lg font-semibold text-gray-900">Day {currentDay.dayNumber}</div>
                <div className="text-gray-600">{formatDayDate(currentDay)}</div>
                <div className="text-sm text-gray-500">{currentDay.year}</div>
              </div>
              
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
              >
                <SortableContext 
                  items={currentDay.items.map(item => item.id)} 
                  strategy={verticalListSortingStrategy}
                >
                  <div className={`space-y-4 transition-all duration-200 ${
                    isReordering ? 'scale-99 opacity-90' : ''
                  }`}>
                    {currentDay.items.map((item) => (
                      <SortableItineraryCard key={item.id} item={item} />
                    ))}
                  </div>
                </SortableContext>
              </DndContext>
            </div>
          </div>
        </div>

        {/* Right Panel - Travel Assistant */}
        {isChatOpen && (
          <div className="w-[480px] bg-white border-l border-gray-200 flex flex-col animate-in slide-in-from-right duration-300">
          {/* Chat Header */}
          <div className="p-6 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-1">
                Travel Assistant
              </h2>
              <p className="text-sm text-gray-600">
                Modify your itinerary
              </p>
            </div>
            <button
              onClick={() => setIsChatOpen(false)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} chat-message-enter`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div
                    className={`max-w-sm px-4 py-3 rounded-lg transition-all duration-200 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white rounded-br-sm'
                        : 'bg-gray-100 text-gray-900 rounded-bl-sm'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      {message.type === 'assistant' ? (
                        <Bot className="h-4 w-4" />
                      ) : (
                        <User className="h-4 w-4" />
                      )}
                    </div>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>
                </div>
              ))}
              
              {/* Typing indicator */}
              {isTyping && (
                <div className="flex justify-start chat-message-enter">
                  <div className="max-w-sm px-4 py-3 rounded-lg bg-gray-100 text-gray-900 rounded-bl-sm">
                    <div className="flex items-center space-x-2 mb-1">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Example Prompts */}
            {messages.length === 1 && (
              <div className="mt-6">
                <p className="text-sm text-gray-600 mb-3">Try asking:</p>
                <div className="space-y-2">
                  {examplePrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => setChatMessage(prompt)}
                      className="w-full text-left p-3 bg-gray-50 rounded-lg border border-gray-200 quick-action-button text-sm text-gray-700"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Ask me to modify your itinerary..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <button
                onClick={handleSendMessage}
                disabled={!chatMessage.trim()}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
          </div>
        )}
        
        {/* Chat Toggle Button - Only show when chat is closed */}
        {!isChatOpen && (
          <div className="fixed bottom-6 right-6">
            <button
              onClick={() => setIsChatOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all duration-200 hover:scale-105"
              aria-label="Open chat"
            >
              <Bot className="w-6 h-6" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};