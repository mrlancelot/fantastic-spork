import { useState, useEffect, useRef } from 'react';
import { 
  Plane, 
  MapPin, 
  Calendar, 
  Users, 
  Settings, 
  User, 
  Search,
  Plus,
  Clock,
  Star,
  Map,
  ExternalLink,
  ChevronRight,
  Bot,
  Send,
  Heart,
  Share,
  Download,
  Bell,
  CreditCard
} from 'lucide-react';

function App() {
  const [currentScreen, setCurrentScreen] = useState('home');
  const [searchData, setSearchData] = useState({
    destination: '',
    startDate: '',
    endDate: '',
    travelers: 2
  });

  const [trips] = useState([
    {
      id: '1',
      destination: 'Tokyo, Japan',
      dates: 'Mar 15-22, 2024',
      status: 'upcoming',
      image: 'https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=400',
      travelers: 2
    },
    {
      id: '2',
      destination: 'Paris, France',
      dates: 'Jan 10-17, 2024',
      status: 'past',
      image: 'https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg?auto=compress&cs=tinysrgb&w=400',
      travelers: 3
    }
  ]);

  const [itinerary] = useState([
    {
      id: '1',
      time: '08:00',
      title: 'Flight to Tokyo',
      type: 'flight',
      location: 'JFK Airport',
      bookingLink: '#'
    },
    {
      id: '2',
      time: '14:30',
      title: 'Hotel Check-in',
      type: 'hotel',
      location: 'Shibuya District',
      bookingLink: '#'
    },
    {
      id: '3',
      time: '18:00',
      title: 'Ramen Dinner',
      type: 'restaurant',
      location: 'Ichiran Shibuya',
      bookingLink: '#'
    }
  ]);

  const NavBar = () => (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2 cursor-pointer" onClick={() => setCurrentScreen('home')}>
            <Plane className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">TravelAI</span>
          </div>
          
          <div className="flex items-center space-x-6">
            <button 
              onClick={() => setCurrentScreen('dashboard')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentScreen === 'dashboard' ? 'text-blue-600 bg-blue-50' : 'text-gray-700 hover:text-blue-600'
              }`}
            >
              My Trips
            </button>
            <button 
              onClick={() => setCurrentScreen('guide')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentScreen === 'guide' ? 'text-blue-600 bg-blue-50' : 'text-gray-700 hover:text-blue-600'
              }`}
            >
              Destinations
            </button>
            <button 
              onClick={() => setCurrentScreen('profile')}
              className={`p-2 rounded-full transition-colors ${
                currentScreen === 'profile' ? 'text-blue-600 bg-blue-50' : 'text-gray-700 hover:text-blue-600'
              }`}
            >
              <User className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );

  const Homepage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50">
      <div className="max-w-4xl mx-auto px-4 pt-20 pb-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">Plan Your Perfect Trip</h1>
          <p className="text-xl text-gray-600 mb-8">AI-powered travel planning with personalized itineraries</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Destination</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Where to?"
                  value={searchData.destination}
                  onChange={(e) => setSearchData({...searchData, destination: e.target.value})}
                  className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Check-in</label>
              <div className="relative">
                <Calendar className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="date"
                  value={searchData.startDate}
                  onChange={(e) => setSearchData({...searchData, startDate: e.target.value})}
                  className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Check-out</label>
              <div className="relative">
                <Calendar className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="date"
                  value={searchData.endDate}
                  onChange={(e) => setSearchData({...searchData, endDate: e.target.value})}
                  className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Travelers</label>
              <div className="relative">
                <Users className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <select
                  value={searchData.travelers}
                  onChange={(e) => setSearchData({...searchData, travelers: parseInt(e.target.value)})}
                  className="pl-10 w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={1}>1 person</option>
                  <option value={2}>2 people</option>
                  <option value={3}>3 people</option>
                  <option value={4}>4+ people</option>
                </select>
              </div>
            </div>
          </div>

          <button 
            onClick={() => setCurrentScreen('planning')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <Search className="h-5 w-5" />
            <span>Start Planning with AI</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Bot className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered Planning</h3>
            <p className="text-gray-600">Smart agents research and plan your perfect itinerary</p>
          </div>
          
          <div className="text-center">
            <div className="bg-teal-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Map className="h-8 w-8 text-teal-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Personalized Routes</h3>
            <p className="text-gray-600">Custom itineraries based on your preferences</p>
          </div>
          
          <div className="text-center">
            <div className="bg-orange-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <ExternalLink className="h-8 w-8 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Direct Booking</h3>
            <p className="text-gray-600">Book flights, hotels, and activities instantly</p>
          </div>
        </div>
      </div>
    </div>
  );

  const Dashboard = () => (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Trips</h1>
          <button 
            onClick={() => setCurrentScreen('planning')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>New Trip</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map(trip => (
            <div key={trip.id} className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
              <img src={trip.image} alt={trip.destination} className="w-full h-48 object-cover" />
              <div className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    trip.status === 'upcoming' ? 'bg-green-100 text-green-800' : 
                    trip.status === 'past' ? 'bg-gray-100 text-gray-800' : 
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {trip.status === 'upcoming' ? 'Upcoming' : trip.status === 'past' ? 'Completed' : 'Planning'}
                  </span>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Users className="h-4 w-4 mr-1" />
                    {trip.travelers}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{trip.destination}</h3>
                <p className="text-gray-600 mb-4">{trip.dates}</p>
                
                <div className="flex space-x-2">
                  <button 
                    onClick={() => setCurrentScreen('itinerary')}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors text-sm font-medium"
                  >
                    View Itinerary
                  </button>
                  <button className="flex-1 border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 px-4 rounded-lg transition-colors text-sm font-medium">
                    Edit Trip
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const PlanningInterface = () => {
    const [step, setStep] = useState(1);
    const [chatMessage, setChatMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([
      { role: 'assistant', content: "Hi! I'm your AI travel assistant. Tell me about your dream trip to Tokyo!" }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const chatContainerRef = useRef(null);
    
    // Auto-scroll to bottom when new messages are added
    useEffect(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    }, [chatHistory]);
    
    const sendMessage = async () => {
      if (!chatMessage.trim() || isLoading) return;
      
      const userMessage = chatMessage;
      setChatMessage('');
      
      // Add user message to chat history
      setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
      
      setIsLoading(true);
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Add AI response to chat history
        setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
      } catch (error) {
        console.error('Error sending message:', error);
        setChatHistory(prev => [...prev, { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error. Please try again.' 
        }]);
      } finally {
        setIsLoading(false);
      }
    };
    
    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    };
    
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Plan Your Trip</h1>
            <div className="flex items-center space-x-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className={`flex items-center ${i < 4 ? 'flex-1' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step >= i ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {i}
                  </div>
                  {i < 4 && <div className={`flex-1 h-1 mx-2 ${step > i ? 'bg-blue-600' : 'bg-gray-200'}`} />}
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-6">Travel Preferences</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Trip Type</label>
                  <div className="grid grid-cols-2 gap-3">
                    {['Adventure', 'Relaxation', 'Culture', 'Business'].map(type => (
                      <button key={type} className="p-3 border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left">
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Budget Range</label>
                  <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option>Budget ($50-100/day)</option>
                    <option>Mid-range ($100-200/day)</option>
                    <option>Luxury ($200+/day)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Interests</label>
                  <div className="flex flex-wrap gap-2">
                    {['Food', 'Museums', 'Nightlife', 'Nature', 'Shopping', 'History'].map(interest => (
                      <button key={interest} className="px-3 py-2 bg-gray-100 hover:bg-blue-100 text-sm rounded-full transition-colors">
                        {interest}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <button 
                onClick={() => setCurrentScreen('itinerary')}
                className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                Generate Itinerary
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Bot className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-semibold">AI Travel Assistant</h2>
              </div>
              
              <div ref={chatContainerRef} className="h-80 bg-gray-50 rounded-lg p-4 mb-4 overflow-y-auto">
                <div className="space-y-4">
                  {chatHistory.map((message, index) => (
                    <div key={index} className={`flex items-start space-x-3 ${message.role === 'user' ? 'justify-end' : ''}`}>
                      {message.role === 'assistant' && (
                        <div className="bg-blue-600 rounded-full p-2">
                          <Bot className="h-4 w-4 text-white" />
                        </div>
                      )}
                      <div className={`rounded-lg p-3 shadow-sm max-w-xs ${
                        message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                      </div>
                      {message.role === 'user' && (
                        <div className="bg-gray-300 rounded-full p-2">
                          <User className="h-4 w-4 text-gray-600" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex items-start space-x-3">
                      <div className="bg-blue-600 rounded-full p-2">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-white rounded-lg p-3 shadow-sm">
                        <p className="text-sm text-gray-500">Typing...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex space-x-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about your trip..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isLoading}
                />
                <button 
                  onClick={sendMessage}
                  disabled={isLoading || !chatMessage.trim()}
                  className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const ItineraryView = () => (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tokyo Adventure</h1>
            <p className="text-gray-600">March 15-22, 2024 • 2 travelers</p>
          </div>
          <div className="flex space-x-3">
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Share className="h-4 w-4" />
              <span>Share</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Heart className="h-4 w-4" />
              <span>Save</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Day 1 - March 15</h2>
              <div className="space-y-4">
                {itinerary.map(item => (
                  <div key={item.id} className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                    <div className="text-sm font-medium text-blue-600 min-w-[60px]">{item.time}</div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{item.title}</h3>
                        {item.type === 'flight' && <Plane className="h-4 w-4 text-blue-600" />}
                        {item.type === 'hotel' && <MapPin className="h-4 w-4 text-green-600" />}
                        {item.type === 'restaurant' && <Star className="h-4 w-4 text-orange-600" />}
                      </div>
                      <p className="text-gray-600 text-sm mb-2">{item.location}</p>
                      {item.bookingLink && (
                        <button className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-sm font-medium">
                          <ExternalLink className="h-4 w-4" />
                          <span>Book Now</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Day 2 - March 16</h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg">
                  <div className="text-sm font-medium text-blue-600 min-w-[60px]">09:00</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">Senso-ji Temple Visit</h3>
                    <p className="text-gray-600 text-sm">Asakusa District</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg">
                  <div className="text-sm font-medium text-blue-600 min-w-[60px]">12:00</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">Sushi Lunch</h3>
                    <p className="text-gray-600 text-sm">Tsukiji Outer Market</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Trip Overview</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Duration</span>
                  <span className="font-medium">7 days</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Travelers</span>
                  <span className="font-medium">2 people</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Budget</span>
                  <span className="font-medium">$2,400</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Activities</span>
                  <span className="font-medium">12 planned</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Map View</h3>
              <div className="bg-gray-200 rounded-lg h-48 flex items-center justify-center">
                <Map className="h-8 w-8 text-gray-400" />
              </div>
              <button className="w-full mt-4 border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 px-4 rounded-lg transition-colors">
                View Full Map
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors">
                  Book All Activities
                </button>
                <button className="w-full border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 px-4 rounded-lg transition-colors">
                  Modify Itinerary
                </button>
                <button className="w-full border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 px-4 rounded-lg transition-colors">
                  Add to Calendar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const DestinationGuide = () => (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Destination Guide</h1>
          <div className="flex space-x-4">
            <input
              type="text"
              placeholder="Search destinations..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors">
              <Search className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-md overflow-hidden mb-6">
              <img 
                src="https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=800" 
                alt="Tokyo skyline"
                className="w-full h-64 object-cover"
              />
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Tokyo, Japan</h2>
                <p className="text-gray-600 mb-4">Experience the perfect blend of traditional culture and modern innovation in Japan's bustling capital.</p>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Best Time to Visit</h4>
                    <p className="text-sm text-gray-600">March-May, September-November</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Average Budget</h4>
                    <p className="text-sm text-gray-600">$150-300 per day</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Language</h4>
                    <p className="text-sm text-gray-600">Japanese</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Currency</h4>
                    <p className="text-sm text-gray-600">Japanese Yen (¥)</p>
                  </div>
                </div>

                <button 
                  onClick={() => setCurrentScreen('planning')}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                >
                  Plan Trip to Tokyo
                </button>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Top Attractions</h3>
              <div className="space-y-4">
                {[
                  { name: 'Senso-ji Temple', type: 'Cultural', rating: 4.8 },
                  { name: 'Tokyo Skytree', type: 'Landmark', rating: 4.7 },
                  { name: 'Shibuya Crossing', type: 'Experience', rating: 4.6 },
                  { name: 'Meiji Shrine', type: 'Cultural', rating: 4.5 }
                ].map(attraction => (
                  <div key={attraction.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                    <div>
                      <h4 className="font-semibold text-gray-900">{attraction.name}</h4>
                      <p className="text-sm text-gray-600">{attraction.type}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="flex items-center space-x-1">
                        <Star className="h-4 w-4 text-yellow-400 fill-current" />
                        <span className="text-sm font-medium">{attraction.rating}</span>
                      </div>
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        Add to Trip
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Popular Destinations</h3>
              <div className="space-y-3">
                {[
                  { name: 'Paris, France', image: 'https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg?auto=compress&cs=tinysrgb&w=200' },
                  { name: 'New York, USA', image: 'https://images.pexels.com/photos/466685/pexels-photo-466685.jpeg?auto=compress&cs=tinysrgb&w=200' },
                  { name: 'Bali, Indonesia', image: 'https://images.pexels.com/photos/2166559/pexels-photo-2166559.jpeg?auto=compress&cs=tinysrgb&w=200' }
                ].map(dest => (
                  <div key={dest.name} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <img src={dest.image} alt={dest.name} className="w-12 h-12 rounded-lg object-cover" />
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{dest.name}</h4>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Travel Tips</h3>
              <div className="space-y-3">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-1">Transportation</h4>
                  <p className="text-sm text-blue-700">Get a JR Pass for unlimited train travel</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-1">Cultural</h4>
                  <p className="text-sm text-green-700">Learn basic Japanese phrases</p>
                </div>
                <div className="p-3 bg-orange-50 rounded-lg">
                  <h4 className="font-medium text-orange-900 mb-1">Money</h4>
                  <p className="text-sm text-orange-700">Cash is still widely used</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const UserProfile = () => (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile & Settings</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="text-center mb-6">
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="h-12 w-12 text-blue-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">John Doe</h2>
              <p className="text-gray-600">john.doe@email.com</p>
            </div>

            <div className="space-y-3">
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3">
                <User className="h-5 w-5 text-gray-400" />
                <span>Edit Profile</span>
              </button>
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3">
                <Bell className="h-5 w-5 text-gray-400" />
                <span>Notifications</span>
              </button>
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3">
                <CreditCard className="h-5 w-5 text-gray-400" />
                <span>Payment Methods</span>
              </button>
              <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3">
                <Settings className="h-5 w-5 text-gray-400" />
                <span>Account Settings</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Travel Preferences</h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Trip Types</label>
                  <div className="flex flex-wrap gap-2">
                    {['Adventure', 'Culture', 'Relaxation', 'Business', 'Food & Wine'].map(type => (
                      <button key={type} className="px-3 py-2 bg-blue-100 text-blue-800 text-sm rounded-full">
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Budget Range</label>
                  <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option>Mid-range ($100-200/day)</option>
                    <option>Budget ($50-100/day)</option>
                    <option>Luxury ($200+/day)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Accommodation Type</label>
                  <div className="grid grid-cols-2 gap-3">
                    {['Hotels', 'Hostels', 'Apartments', 'Resorts'].map(type => (
                      <button key={type} className="p-3 border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left">
                        {type}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <button className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors">
                Save Preferences
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Notification Settings</h3>
              
              <div className="space-y-4">
                {[
                  { title: 'Trip Updates', description: 'Get notified about changes to your itinerary' },
                  { title: 'Booking Confirmations', description: 'Receive confirmations for reservations' },
                  { title: 'Deal Alerts', description: 'Special offers for your favorite destinations' },
                  { title: 'Travel Tips', description: 'Helpful tips and recommendations' }
                ].map(setting => (
                  <div key={setting.title} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{setting.title}</h4>
                      <p className="text-sm text-gray-600">{setting.description}</p>
                    </div>
                    <div className="flex items-center">
                      <input type="checkbox" className="h-5 w-5 text-blue-600 rounded" defaultChecked />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'home': return <Homepage />;
      case 'dashboard': return <Dashboard />;
      case 'planning': return <PlanningInterface />;
      case 'itinerary': return <ItineraryView />;
      case 'guide': return <DestinationGuide />;
      case 'profile': return <UserProfile />;
      default: return <Homepage />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <NavBar />
      {renderCurrentScreen()}
    </div>
  );
}

export default App;