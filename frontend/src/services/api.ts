// API Service Layer with Type Safety
// Handles all communication with the backend

// Types matching backend schema exactly
export interface ItineraryRequest {
  trip_type: 'round_trip' | 'one_way';
  from_city: string;
  to_city: string;
  departure_date: string; // Format: YYYY-MM-DD
  return_date?: string;    // Format: YYYY-MM-DD (optional for one-way)
  adults: number;
  travel_class: 'economy' | 'premium_economy' | 'business' | 'first';
  interests: string;       // Free text string
  price_range?: 'budget' | 'mid_range' | 'upscale';
}

export interface ItineraryActivity {
  time: string;
  title: string;
  description: string;
  location?: string;
  duration?: string;
  activity_type: 'flight' | 'hotel' | 'meal' | 'activity' | 'transport';
  additional_info?: string;
}

export interface DayItinerary {
  day_number: number;
  date: string;
  year: number;
  activities: ItineraryActivity[];
}

export interface TripDetails {
  trip_type: string;
  route: string;
  departure_date: string;
  return_date?: string;
  passengers: number;
  travel_class: string;
  interests: string;
  price_range?: string;
}

export interface ItineraryResponse {
  status: string;
  title: string;
  personalization: string;
  total_days: number;
  days: DayItinerary[];
  trip_details?: TripDetails;
  message?: string;
}

// Get API URL from environment or default to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to handle API errors
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

// Main API function to create itinerary
export async function createItinerary(data: ItineraryRequest): Promise<ItineraryResponse> {
  try {
    console.log('Sending itinerary request:', data);
    
    // Use the main itinerary endpoint
    const response = await fetch(`${API_URL}/itinerary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error Response:', errorText);
      throw new APIError(response.status, `Failed to create itinerary: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('Itinerary created successfully:', result);
    return result;
  } catch (error) {
    console.error('API call failed:', error);
    
    // Re-throw API errors
    if (error instanceof APIError) {
      throw error;
    }
    
    // Network or other errors
    throw new Error('Failed to connect to the server. Please check your connection and try again.');
  }
}

// Health check endpoint
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}

// Helper function to map frontend budget to backend price_range
export function mapBudgetToPriceRange(budget: string): 'budget' | 'mid_range' | 'upscale' {
  const mapping: Record<string, 'budget' | 'mid_range' | 'upscale'> = {
    'budget': 'budget',
    'moderate': 'mid_range',
    'luxury': 'upscale'
  };
  return mapping[budget] || 'mid_range';
}

// Helper function to format date for backend (YYYY-MM-DD)
export function formatDateForAPI(date: Date | null): string | undefined {
  if (!date) return undefined;
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

// Map backend activity type to frontend type
export function mapActivityType(backendType: string): 'sightseeing' | 'restaurant' | 'hotel' | 'transport' | 'activity' {
  const mapping: Record<string, 'sightseeing' | 'restaurant' | 'hotel' | 'transport' | 'activity'> = {
    'flight': 'transport',
    'hotel': 'hotel',
    'meal': 'restaurant',
    'activity': 'sightseeing',
    'transport': 'transport'
  };
  return mapping[backendType] || 'activity';
}