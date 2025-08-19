import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import Fuse from 'fuse.js';
import { majorCities, City } from '../data/cities';

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
  const [searchTerm, setSearchTerm] = useState(value);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [loadedCities, setLoadedCities] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Initialize Fuse.js with lazy loading
  const fuse = useMemo(() => {
    if (!loadedCities) return null;
    
    return new Fuse(majorCities, {
      keys: ['name', 'country'],
      threshold: 0.4, // Balanced fuzzy matching
      includeScore: true,
      shouldSort: true,
      minMatchCharLength: 1,
    });
  }, [loadedCities]);

  // Load cities when user starts typing (lazy loading)
  useEffect(() => {
    if (searchTerm.length >= 4 && !loadedCities && !isLoading) {
      setIsLoading(true);
      // Simulate async loading (in reality, cities are already imported)
      setTimeout(() => {
        setLoadedCities(true);
        setIsLoading(false);
      }, 100);
    }
  }, [searchTerm, loadedCities, isLoading]);

  // Get filtered results
  const getFilteredCities = useCallback((): City[] => {
    if (!fuse || searchTerm.length < 4) return [];
    
    const results = fuse.search(searchTerm);
    // Return top 5 results
    return results.slice(0, 5).map(result => result.item);
  }, [fuse, searchTerm]);

  const filteredCities = useMemo(() => getFilteredCities(), [getFilteredCities]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setSearchTerm(newValue);
    setSelectedIndex(-1);
    
    if (newValue.length >= 4) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
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
          prev < filteredCities.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredCities.length) {
          selectCity(filteredCities[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
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

  // Sync internal state with external value prop
  useEffect(() => {
    setSearchTerm(value);
  }, [value]);

  // Group cities by country for display
  const groupedCities = useMemo(() => {
    const groups: { [country: string]: City[] } = {};
    filteredCities.forEach(city => {
      if (!groups[city.country]) {
        groups[city.country] = [];
      }
      groups[city.country].push(city);
    });
    return groups;
  }, [filteredCities]);

  return (
    <div ref={containerRef} className="relative">
      {label && (
        <label htmlFor={id} className="block text-xs font-medium text-neutral-500 uppercase mb-2">
          {label}
        </label>
      )}
      <input
        ref={inputRef}
        id={id}
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => {
          if (searchTerm.length >= 4 && filteredCities.length > 0) {
            setIsOpen(true);
          }
        }}
        placeholder={placeholder}
        required={required}
        className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        autoComplete="off"
      />
      
      {/* Loading indicator */}
      {isLoading && searchTerm.length >= 4 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg py-2 px-3">
          <div className="text-sm text-neutral-500">Loading cities...</div>
        </div>
      )}
      
      {/* Dropdown */}
      {isOpen && !isLoading && filteredCities.length > 0 && (
        <div 
          ref={dropdownRef}
          className="absolute z-10 w-full mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg max-h-60 overflow-auto"
        >
          <ul className="py-1">
            {filteredCities.map((city, index) => (
              <li key={`${city.name}-${city.country}`}>
                <button
                  type="button"
                  onClick={() => selectCity(city)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`w-full text-left px-3 py-2 text-sm transition-colors ${
                    index === selectedIndex
                      ? 'bg-primary-50 text-primary-900'
                      : 'text-neutral-700 hover:bg-neutral-50'
                  }`}
                >
                  <span className="font-medium">{city.name}</span>
                  <span className="text-neutral-500">, {city.country}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* No results message */}
      {isOpen && !isLoading && searchTerm.length >= 4 && filteredCities.length === 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg py-2 px-3">
          <div className="text-sm text-neutral-500">No cities found</div>
        </div>
      )}
    </div>
  );
};