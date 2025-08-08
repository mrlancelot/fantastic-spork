import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, MapPin, Calendar, DollarSign, Users, Heart } from 'lucide-react';

const AgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [tripConfig, setTripConfig] = useState({
    destination: '',
    start_date: '',
    end_date: '',
    origin: 'New York',
    budget: 5000,
    travelers: 1,
    interests: []
  });
  const [showConfig, setShowConfig] = useState(true);
  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);

  const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (action, content, service = null, data = null) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      action,
      content,
      service,
      data,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const handlePlanTrip = async () => {
    if (!tripConfig.destination || !tripConfig.start_date || !tripConfig.end_date) {
      alert('Please fill in destination and dates');
      return;
    }

    setShowConfig(false);
    setIsStreaming(true);
    setMessages([]);

    try {
      const response = await fetch(`${API_BASE}/api/agent/plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tripConfig)
      });

      if (!response.ok) throw new Error('Failed to start planning');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setIsStreaming(false);
              break;
            }

            try {
              const thought = JSON.parse(data);
              addMessage(thought.action, thought.content, thought.service, thought.data);
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      addMessage('error', `Error: ${error.message}`);
      setIsStreaming(false);
    }
  };

  const handleQuickSearch = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    addMessage('user', userMessage);
    setIsStreaming(true);

    try {
      const response = await fetch(`${API_BASE}/api/agent/quick-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await response.json();
      addMessage('complete', data.response);
    } catch (error) {
      addMessage('error', `Error: ${error.message}`);
    } finally {
      setIsStreaming(false);
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'thinking': return '🤔';
      case 'searching': return '🔍';
      case 'analyzing': return '📊';
      case 'calling_service': return '⚙️';
      case 'complete': return '✅';
      case 'error': return '❌';
      case 'user': return '👤';
      default: return '💬';
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'thinking': return 'bg-blue-50 border-blue-200';
      case 'searching': return 'bg-purple-50 border-purple-200';
      case 'analyzing': return 'bg-green-50 border-green-200';
      case 'calling_service': return 'bg-yellow-50 border-yellow-200';
      case 'complete': return 'bg-emerald-50 border-emerald-200';
      case 'error': return 'bg-red-50 border-red-200';
      case 'user': return 'bg-gray-50 border-gray-200';
      default: return 'bg-white border-gray-200';
    }
  };

  const interestOptions = ['food', 'culture', 'adventure', 'relaxation', 'shopping', 'nightlife', 'nature', 'history'];

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-lg">
          <h1 className="text-2xl font-bold">TravelAI Smart Agent</h1>
          <p className="text-blue-100">Powered by GLM-4.5 with real-time web search</p>
        </div>

        {showConfig ? (
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Plan Your Trip</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <MapPin className="inline w-4 h-4 mr-1" />
                  Destination
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Tokyo, Paris, New York"
                  value={tripConfig.destination}
                  onChange={(e) => setTripConfig({...tripConfig, destination: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <MapPin className="inline w-4 h-4 mr-1" />
                  Origin
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., New York"
                  value={tripConfig.origin}
                  onChange={(e) => setTripConfig({...tripConfig, origin: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar className="inline w-4 h-4 mr-1" />
                  Start Date
                </label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={tripConfig.start_date}
                  onChange={(e) => setTripConfig({...tripConfig, start_date: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar className="inline w-4 h-4 mr-1" />
                  End Date
                </label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={tripConfig.end_date}
                  onChange={(e) => setTripConfig({...tripConfig, end_date: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <DollarSign className="inline w-4 h-4 mr-1" />
                  Budget
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="5000"
                  value={tripConfig.budget}
                  onChange={(e) => setTripConfig({...tripConfig, budget: parseInt(e.target.value)})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Users className="inline w-4 h-4 mr-1" />
                  Travelers
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  value={tripConfig.travelers}
                  onChange={(e) => setTripConfig({...tripConfig, travelers: parseInt(e.target.value)})}
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Heart className="inline w-4 h-4 mr-1" />
                  Interests
                </label>
                <div className="flex flex-wrap gap-2">
                  {interestOptions.map(interest => (
                    <button
                      key={interest}
                      onClick={() => {
                        const interests = tripConfig.interests.includes(interest)
                          ? tripConfig.interests.filter(i => i !== interest)
                          : [...tripConfig.interests, interest];
                        setTripConfig({...tripConfig, interests});
                      }}
                      className={`px-3 py-1 rounded-full text-sm ${
                        tripConfig.interests.includes(interest)
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={handlePlanTrip}
              disabled={isStreaming}
              className="mt-6 w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-md hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {isStreaming ? (
                <span className="flex items-center justify-center">
                  <Loader2 className="animate-spin mr-2" />
                  Planning...
                </span>
              ) : (
                'Start Planning My Trip'
              )}
            </button>
          </div>
        ) : (
          <div className="flex flex-col h-[600px]">
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`p-3 rounded-lg border ${getActionColor(message.action)}`}
                >
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">{getActionIcon(message.action)}</span>
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        <span className="font-semibold capitalize">
                          {message.action.replace('_', ' ')}
                        </span>
                        {message.service && (
                          <span className="ml-2 text-xs bg-gray-200 px-2 py-1 rounded">
                            {message.service}
                          </span>
                        )}
                        <span className="ml-auto text-xs text-gray-500">
                          {message.timestamp}
                        </span>
                      </div>
                      <div className="text-gray-700 whitespace-pre-wrap">
                        {message.content}
                      </div>
                      {message.data && (
                        <div className="mt-2 p-2 bg-white bg-opacity-50 rounded">
                          <pre className="text-xs overflow-x-auto">
                            {JSON.stringify(message.data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t p-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuickSearch()}
                  placeholder="Ask a quick question..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isStreaming}
                />
                <button
                  onClick={handleQuickSearch}
                  disabled={isStreaming || !input.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  <Send className="w-5 h-5" />
                </button>
                <button
                  onClick={() => {
                    setShowConfig(true);
                    setMessages([]);
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                  New Trip
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentChat;