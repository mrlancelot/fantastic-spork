import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X, Minimize2, Maximize2, Bot, User, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

const quickSuggestions = [
  "Find restaurants nearby",
  "What's the weather like?",
  "Show me local activities",
  "Plan my next slot",
  "Book a hotel",
  "Flight status updates",
  "Cultural tips for this area",
  "Best photo spots",
];

const aiPersonalities = {
  helpful: {
    name: "Alex",
    avatar: "🤖",
    description: "Your helpful travel assistant"
  },
  local: {
    name: "Maya",
    avatar: "🗺️", 
    description: "Local expert and cultural guide"
  },
  adventure: {
    name: "Zoe",
    avatar: "🎯",
    description: "Adventure planning specialist"
  },
  foodie: {
    name: "Chef",
    avatar: "👨‍🍳",
    description: "Food and dining expert"
  }
};

function ChatMessage({ message, isUser, isTyping = false }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-lg">
          🤖
        </div>
      )}
      
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
        isUser 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        {isTyping ? (
          <div className="flex items-center gap-1">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
            <span className="text-sm text-gray-500 ml-2">AI is thinking...</span>
          </div>
        ) : (
          <div className="text-sm whitespace-pre-wrap">{message.content}</div>
        )}
        
        <div className={`text-xs mt-1 opacity-75 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
      
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-lg">
          👤
        </div>
      )}
    </motion.div>
  );
}

function QuickSuggestion({ text, onClick }) {
  return (
    <button
      onClick={() => onClick(text)}
      className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors whitespace-nowrap"
    >
      {text}
    </button>
  );
}

export default function AIChat({ tripId, currentLocation }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! I\'m your AI travel assistant. I can help you find restaurants, activities, check weather, book hotels, and more! What would you like to explore?',
      timestamp: Date.now()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPersonality, setSelectedPersonality] = useState('helpful');
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, isMinimized]);

  const sendMessage = async (text = inputText) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: text.trim(),
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Add context about current trip and location
      const context = {
        tripId,
        currentLocation,
        personality: selectedPersonality,
        previousMessages: messages.slice(-5) // Last 5 messages for context
      };

      const response = await fetch(`${API_BASE}/api/chat/agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: text.trim(),
          context 
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();

      const aiMessage = {
        role: 'assistant',
        content: data.response || "I'm here to help! Could you please rephrase your question?",
        timestamp: Date.now(),
        context: data.context
      };

      setMessages(prev => [...prev, aiMessage]);

      // If the AI provided actionable suggestions, show them
      if (data.context?.suggestions) {
        setTimeout(() => {
          const suggestionMessage = {
            role: 'assistant',
            content: `Here are some suggestions based on your request:\n\n${data.context.suggestions.join('\n• ')}`,
            timestamp: Date.now()
          };
          setMessages(prev => [...prev, suggestionMessage]);
        }, 1000);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: "I'm having trouble connecting right now. Please try again in a moment, or let me know if you need help with something specific!",
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, errorMessage]);
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

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Chat cleared! How can I help you with your travel plans?',
      timestamp: Date.now()
    }]);
  };

  // Floating chat button
  if (!isOpen) {
    return (
      <motion.button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center z-50 transition-colors"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
      >
        <MessageCircle className="w-6 h-6" />
        
        {/* Notification dot for new features */}
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
          <Zap className="w-2 h-2 text-white" />
        </div>
      </motion.button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ 
        opacity: 1, 
        scale: 1, 
        y: 0,
        height: isMinimized ? '60px' : '500px'
      }}
      className="fixed bottom-6 right-6 w-80 bg-white rounded-lg shadow-2xl border border-gray-200 z-50 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-lg">{aiPersonalities[selectedPersonality].avatar}</div>
          <div>
            <h3 className="font-semibold">{aiPersonalities[selectedPersonality].name}</h3>
            <p className="text-xs opacity-90">{aiPersonalities[selectedPersonality].description}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {!isMinimized && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {/* Personality Selector */}
            <div className="p-3 border-b border-gray-100">
              <div className="flex gap-2 overflow-x-auto">
                {Object.entries(aiPersonalities).map(([key, personality]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedPersonality(key)}
                    className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                      selectedPersonality === key
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    <span>{personality.avatar}</span>
                    <span>{personality.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Messages */}
            <div className="h-64 overflow-y-auto p-4 space-y-2">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                  isUser={message.role === 'user'}
                />
              ))}
              
              {isLoading && (
                <ChatMessage
                  message={{ content: '', timestamp: Date.now() }}
                  isUser={false}
                  isTyping={true}
                />
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestions */}
            {messages.length <= 2 && (
              <div className="px-4 pb-2">
                <p className="text-xs text-gray-500 mb-2">Quick suggestions:</p>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {quickSuggestions.slice(0, 4).map((suggestion, index) => (
                    <QuickSuggestion
                      key={index}
                      text={suggestion}
                      onClick={sendMessage}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-gray-100">
              <div className="flex items-center gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about your trip..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
                  disabled={isLoading}
                />
                <button
                  onClick={() => sendMessage()}
                  disabled={!inputText.trim() || isLoading}
                  className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              
              <div className="flex items-center justify-between mt-2">
                <button
                  onClick={clearChat}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  Clear chat
                </button>
                <div className="text-xs text-gray-400">
                  Powered by AI • Real-time
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}