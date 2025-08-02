import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Send, User, Sparkles, Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from './Button';

const quickReplies = [
  "Suggest budget-friendly options",
  "What's the best time to visit?",
  "Recommend local cuisine",
  "Find adventure activities",
  "Plan a romantic getaway",
];

export function ChatInterface({ onSendMessage, className }) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      role: 'assistant', 
      content: "Hi! I'm your AI travel assistant. Tell me about your dream trip and I'll help you plan it perfectly! ✈️",
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);
    setMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: onSendMessage ? onSendMessage(message) : "That sounds amazing! Let me help you plan that perfect trip...",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleQuickReply = (reply) => {
    setMessage(reply);
    inputRef.current?.focus();
  };

  return (
    <motion.div
      className={cn(
        "flex flex-col h-full bg-white rounded-2xl shadow-xl overflow-hidden",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 p-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white" />
          </div>
          <div className="flex-1 text-white">
            <h3 className="font-semibold">AI Travel Assistant</h3>
            <p className="text-sm text-white/80 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Powered by Advanced AI
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-neutral-50"
      >
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={cn(
                "flex items-start gap-3",
                msg.role === 'user' && "flex-row-reverse"
              )}
            >
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                msg.role === 'assistant' 
                  ? "bg-gradient-to-br from-primary-500 to-secondary-500"
                  : "bg-neutral-300"
              )}>
                {msg.role === 'assistant' ? (
                  <Bot className="w-4 h-4 text-white" />
                ) : (
                  <User className="w-4 h-4 text-neutral-600" />
                )}
              </div>
              
              <motion.div
                className={cn(
                  "max-w-[70%] rounded-2xl px-4 py-3 shadow-sm",
                  msg.role === 'assistant'
                    ? "bg-white text-neutral-800"
                    : "bg-gradient-to-r from-primary-600 to-secondary-600 text-white"
                )}
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              >
                <p className="text-sm leading-relaxed">{msg.content}</p>
                <span className={cn(
                  "text-xs mt-1 block",
                  msg.role === 'assistant' ? "text-neutral-400" : "text-white/70"
                )}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </motion.div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-start gap-3"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex items-center gap-1">
                  <motion.div
                    className="w-2 h-2 bg-neutral-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-neutral-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-neutral-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Quick Replies */}
      <div className="p-3 border-t border-neutral-200">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          {quickReplies.map((reply, index) => (
            <motion.button
              key={index}
              className="flex-shrink-0 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm hover:bg-primary-100 transition-colors"
              onClick={() => handleQuickReply(reply)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {reply}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-neutral-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex gap-2"
        >
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me anything about your trip..."
            className="flex-1 px-4 py-3 bg-neutral-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
          />
          <Button
            type="submit"
            variant="gradient"
            size="md"
            disabled={!message.trim() || isTyping}
            className="px-6"
          >
            {isTyping ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </form>
      </div>
    </motion.div>
  );
}