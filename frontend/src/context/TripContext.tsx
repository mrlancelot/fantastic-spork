import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ItineraryResponse } from '../services/api';

// Extended SearchFormData to include from_city
export interface SearchFormData {
  fromCity: string;      // NEW FIELD
  destination: string;   // to_city in backend
  startDate: Date | null;
  endDate: Date | null;
  travelers: number;
  budget: string;
  interests: string[];
  tripType: 'roundtrip' | 'oneway';
  travelClass: 'economy' | 'premium_economy' | 'business' | 'first';
}

interface TripContextType {
  formData: SearchFormData | null;
  itineraryData: ItineraryResponse | null;
  setFormData: (data: SearchFormData) => void;
  setItineraryData: (data: ItineraryResponse) => void;
  clearData: () => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

// Helper functions for localStorage
const STORAGE_KEYS = {
  FORM_DATA: 'tripFormData',
  ITINERARY_DATA: 'itineraryData',
};

const saveToStorage = (key: string, data: any) => {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.error('Failed to save to localStorage:', error);
  }
};

const loadFromStorage = (key: string) => {
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Failed to load from localStorage:', error);
    return null;
  }
};

const removeFromStorage = (key: string) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Failed to remove from localStorage:', error);
  }
};

// Create context
const TripContext = createContext<TripContextType | undefined>(undefined);

// Provider component
export const TripProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [formData, setFormDataState] = useState<SearchFormData | null>(null);
  const [itineraryData, setItineraryDataState] = useState<ItineraryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load data from localStorage on mount
  useEffect(() => {
    const savedFormData = loadFromStorage(STORAGE_KEYS.FORM_DATA);
    const savedItineraryData = loadFromStorage(STORAGE_KEYS.ITINERARY_DATA);
    
    if (savedFormData) {
      // Parse dates back to Date objects
      if (savedFormData.startDate) {
        savedFormData.startDate = new Date(savedFormData.startDate);
      }
      if (savedFormData.endDate) {
        savedFormData.endDate = new Date(savedFormData.endDate);
      }
      setFormDataState(savedFormData);
    }
    
    if (savedItineraryData) {
      setItineraryDataState(savedItineraryData);
    }
  }, []);

  // Save form data to localStorage and state
  const setFormData = (data: SearchFormData) => {
    setFormDataState(data);
    saveToStorage(STORAGE_KEYS.FORM_DATA, data);
    // Clear any previous error when new form data is set
    setError(null);
  };

  // Save itinerary data to localStorage and state
  const setItineraryData = (data: ItineraryResponse) => {
    setItineraryDataState(data);
    saveToStorage(STORAGE_KEYS.ITINERARY_DATA, data);
    // Clear loading and error states
    setIsLoading(false);
    setError(null);
  };

  // Clear all data
  const clearData = () => {
    setFormDataState(null);
    setItineraryDataState(null);
    setIsLoading(false);
    setError(null);
    removeFromStorage(STORAGE_KEYS.FORM_DATA);
    removeFromStorage(STORAGE_KEYS.ITINERARY_DATA);
  };

  const value: TripContextType = {
    formData,
    itineraryData,
    setFormData,
    setItineraryData,
    clearData,
    isLoading,
    setIsLoading,
    error,
    setError,
  };

  return <TripContext.Provider value={value}>{children}</TripContext.Provider>;
};

// Custom hook to use the context
export const useTripContext = () => {
  const context = useContext(TripContext);
  if (context === undefined) {
    throw new Error('useTripContext must be used within a TripProvider');
  }
  return context;
};

// Export default for convenience
export default TripContext;