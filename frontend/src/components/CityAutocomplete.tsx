import React, { useState, useRef, useEffect } from 'react';
import { searchCities, isValidCity, City } from '../data/allCities';

interface CityAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  label?: string;
  id?: string;
}

export const CityAutocomplete: React.FC<CityAutocompleteProps> = ({
  value,
  onChange,
  placeholder = "Where?",
  required = false,
  label,
  id
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState(value || '');
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [filteredCities, setFilteredCities] = useState<City[]>([]);
  const [isValidSelection, setIsValidSelection] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  // Check if current value is a valid selection
  useEffect(() => {
    if (searchTerm) {
      setIsValidSelection(isValidCity(searchTerm));
    } else {
      setIsValidSelection(false);
    }
  }, [searchTerm]);

  // Filter cities based on search term with debouncing
  useEffect(() => {
    // Clear any existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // If it's a valid selection, don't search
    if (isValidSelection) {
      setFilteredCities([]);
      setIsOpen(false);
      setIsSearching(false);
      return;
    }

    if (searchTerm.length < 2) {
      setFilteredCities([]);
      setIsOpen(false);
      setIsSearching(false);
      return;
    }

    // Start searching indicator
    setIsSearching(true);

    // Debounce the search
    searchTimeoutRef.current = setTimeout(() => {
      try {
        const results = searchCities(searchTerm, 10);
        setFilteredCities(results);
        setIsOpen(results.length > 0);
      } catch (error) {
        console.error('Search error:', error);
        setFilteredCities([]);
        setIsOpen(false);
      } finally {
        setIsSearching(false);
      }
    }, 200); // 200ms debounce

    // Cleanup timeout on unmount or when search term changes
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchTerm, isValidSelection]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setSearchTerm(newValue);
    onChange(newValue);
    setSelectedIndex(-1);
  };

  // Handle city selection
  const selectCity = (city: City) => {
    const selectedValue = city.displayName;
    setSearchTerm(selectedValue);
    onChange(selectedValue);
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || filteredCities.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < filteredCities.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : filteredCities.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredCities.length) {
          selectCity(filteredCities[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Sync with external value
  useEffect(() => {
    setSearchTerm(value || '');
  }, [value]);

  return (
    <div ref={containerRef} className="relative w-full">
      {label && (
        <label htmlFor={id} className="block text-xs font-bold mb-1" style={{ color: '#2C3E50' }}>
          {label.toUpperCase()}
        </label>
      )}
      <input
        id={id}
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => {
          // Only open if there are filtered results and not a valid selection
          if (filteredCities.length > 0 && !isValidSelection) {
            setIsOpen(true);
          }
        }}
        placeholder={placeholder}
        required={required}
        className="w-full px-3 py-2.5 text-sm bg-[#F0F0F0] border-2 border-[#2C3E50] rounded-[6px] focus:outline-none focus:ring-2 focus:ring-[#4A90E2] focus:border-transparent transition-all duration-200 hover:bg-[#E8E8E8]"
        autoComplete="off"
      />
      
      {/* Helper text - only show when typing and not enough characters */}
      {searchTerm.length > 0 && searchTerm.length < 2 && !isValidSelection && (
        <div className="absolute z-50 w-full mt-1 bg-yellow-50 border border-yellow-200 rounded-lg shadow-sm py-1 px-2">
          <div className="text-xs text-yellow-700">Type at least 2 characters</div>
        </div>
      )}
      
      {/* Loading indicator */}
      {isSearching && (
        <div className="absolute z-50 w-full mt-1 bg-blue-50 border border-blue-200 rounded-lg shadow-sm py-1 px-2">
          <div className="text-xs text-blue-700">Searching cities...</div>
        </div>
      )}
      
      {/* Dropdown */}
      {isOpen && filteredCities.length > 0 && (
        <div 
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-[#F0F0F0] border-2 border-[#2C3E50] rounded-[6px] shadow-xl max-h-60 overflow-auto"
          style={{ top: '100%', left: 0 }}
        >
          <ul className="py-1">
            {filteredCities.map((city, index) => (
              <li key={`${city.name}-${city.country}-${index}`}>
                <button
                  type="button"
                  onClick={() => selectCity(city)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`w-full text-left px-3 py-2 text-sm transition-colors ${
                    index === selectedIndex
                      ? 'bg-[#4A90E2] text-white'
                      : 'text-[#2C3E50] hover:bg-[#E0E0E0]'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-medium">{city.name}</span>
                      {city.state && (
                        <span className={index === selectedIndex ? 'text-white opacity-90' : 'text-gray-600'}>
                          , {city.state}
                        </span>
                      )}
                      <span className={index === selectedIndex ? 'text-white opacity-90' : 'text-gray-600'}>
                        , {city.country}
                      </span>
                    </div>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* No results - only show when actively searching, not for valid selections */}
      {searchTerm.length >= 2 && filteredCities.length === 0 && !isValidSelection && !isSearching && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-2 px-3">
          <div className="text-sm text-gray-500">No cities found for "{searchTerm}"</div>
        </div>
      )}
    </div>
  );
};