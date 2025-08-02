import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, MapPin, Calendar, Users, X } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from './Button';

const suggestions = [
  { id: 1, name: 'Tokyo, Japan', type: 'city', icon: MapPin },
  { id: 2, name: 'Bali, Indonesia', type: 'city', icon: MapPin },
  { id: 3, name: 'Paris, France', type: 'city', icon: MapPin },
  { id: 4, name: 'New York, USA', type: 'city', icon: MapPin },
  { id: 5, name: 'Dubai, UAE', type: 'city', icon: MapPin },
];

export function SearchBar({ onSearch, className }) {
  const [searchData, setSearchData] = useState({
    destination: '',
    startDate: '',
    endDate: '',
    travelers: 2,
  });
  
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (searchData.destination.length > 1) {
      const filtered = suggestions.filter(s =>
        s.name.toLowerCase().includes(searchData.destination.toLowerCase())
      );
      setFilteredSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  }, [searchData.destination]);

  const handleSearch = () => {
    if (searchData.destination && searchData.startDate && searchData.endDate) {
      onSearch(searchData);
    }
  };

  return (
    <motion.div
      className={cn(
        "relative w-full max-w-4xl mx-auto",
        className
      )}
      animate={{ width: isExpanded ? '100%' : '100%' }}
    >
      <motion.div
        className="bg-white rounded-2xl shadow-2xl p-2 border border-neutral-100"
        layout
      >
        <div className="flex flex-col lg:flex-row gap-2">
          {/* Destination Input */}
          <div className="flex-1 relative">
            <div className="relative">
              <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
              <input
                type="text"
                placeholder="Where to?"
                value={searchData.destination}
                onChange={(e) => setSearchData({ ...searchData, destination: e.target.value })}
                onFocus={() => setIsExpanded(true)}
                className="w-full pl-12 pr-4 py-4 rounded-xl bg-neutral-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
              />
              {searchData.destination && (
                <button
                  onClick={() => setSearchData({ ...searchData, destination: '' })}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-neutral-200 rounded-full transition-colors"
                >
                  <X className="w-4 h-4 text-neutral-500" />
                </button>
              )}
            </div>
            
            {/* Suggestions Dropdown */}
            <AnimatePresence>
              {showSuggestions && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-neutral-100 overflow-hidden z-50"
                >
                  {filteredSuggestions.map((suggestion) => (
                    <motion.button
                      key={suggestion.id}
                      className="w-full px-4 py-3 flex items-center gap-3 hover:bg-primary-50 transition-colors text-left"
                      onClick={() => {
                        setSearchData({ ...searchData, destination: suggestion.name });
                        setShowSuggestions(false);
                      }}
                      whileHover={{ x: 5 }}
                    >
                      <suggestion.icon className="w-5 h-5 text-primary-600" />
                      <span className="text-neutral-800">{suggestion.name}</span>
                    </motion.button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          {/* Date Inputs */}
          <AnimatePresence>
            {isExpanded && (
              <>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="relative"
                >
                  <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
                  <input
                    type="date"
                    value={searchData.startDate}
                    onChange={(e) => setSearchData({ ...searchData, startDate: e.target.value })}
                    className="w-full lg:w-40 pl-12 pr-4 py-4 rounded-xl bg-neutral-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                  />
                </motion.div>
                
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ delay: 0.1 }}
                  className="relative"
                >
                  <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
                  <input
                    type="date"
                    value={searchData.endDate}
                    onChange={(e) => setSearchData({ ...searchData, endDate: e.target.value })}
                    className="w-full lg:w-40 pl-12 pr-4 py-4 rounded-xl bg-neutral-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                  />
                </motion.div>
                
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ delay: 0.2 }}
                  className="relative"
                >
                  <Users className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
                  <select
                    value={searchData.travelers}
                    onChange={(e) => setSearchData({ ...searchData, travelers: parseInt(e.target.value) })}
                    className="w-full lg:w-32 pl-12 pr-4 py-4 rounded-xl bg-neutral-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all appearance-none cursor-pointer"
                  >
                    <option value={1}>1 person</option>
                    <option value={2}>2 people</option>
                    <option value={3}>3 people</option>
                    <option value={4}>4+ people</option>
                  </select>
                </motion.div>
              </>
            )}
          </AnimatePresence>
          
          {/* Search Button */}
          <motion.div
            initial={{ scale: 1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              variant="gradient"
              size="lg"
              onClick={handleSearch}
              className="h-full px-8 shadow-xl"
            >
              <Search className="w-5 h-5" />
              <span className="ml-2 hidden sm:inline">Search</span>
            </Button>
          </motion.div>
        </div>
      </motion.div>
    </motion.div>
  );
}