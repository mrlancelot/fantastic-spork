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

// Job response types
export interface JobCreationResponse {
  status: string;
  job_id: string;
  itinerary_uuid: string;
  message: string;
  polling_interval_seconds: number;
}

export interface JobProgress {
  message: string;
  step: 'initializing' | 'flights' | 'hotels' | 'restaurants' | 'activities' | 'completing';
  details: {
    flights_found: number;
    hotels_found: number;
    restaurants_found: number;
    activities_planned: number;
    price_ranges: {
      flights?: { min: number; max: number };
      hotels?: { min: number; max: number };
    };
  };
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: number;
  started_at?: number;
  completed_at?: number;
  error?: string;
  progress?: JobProgress;
  result?: {
    itinerary_id: string;
    itinerary_uuid: string;
    activity_count: number;
    flight_count: number;
    hotel_count: number;
  };
  next_step?: string;
}

// Create async itinerary job
export async function createItineraryJob(data: ItineraryRequest): Promise<JobCreationResponse> {
  try {
    console.log('Creating itinerary job:', data);
    
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
      throw new APIError(response.status, `Failed to create itinerary job: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('Job created successfully:', result);
    return result;
  } catch (error) {
    console.error('API call failed:', error);
    
    if (error instanceof APIError) {
      throw error;
    }
    
    throw new Error('Failed to connect to the server. Please check your connection and try again.');
  }
}

// Check job status
export async function checkJobStatus(jobId: string): Promise<JobStatusResponse> {
  try {
    const response = await fetch(`${API_URL}/itinerary/status/${jobId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new APIError(response.status, `Failed to check job status: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Status check failed:', error);
    
    if (error instanceof APIError) {
      throw error;
    }
    
    throw new Error('Failed to check job status.');
  }
}

// Get complete itinerary
export async function getItinerary(itineraryUuid: string): Promise<ItineraryResponse> {
  try {
    const response = await fetch(`${API_URL}/itinerary/${itineraryUuid}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new APIError(response.status, `Failed to fetch itinerary: ${response.statusText}`);
    }

    const result = await response.json();
    
    // Extract the itinerary data from the response
    if (result.status === 'success' && result.itinerary) {
      // Map backend response to expected format
      const itinerary = result.itinerary;
      return {
        status: 'success',
        title: itinerary.data?.title || 'Your Travel Itinerary',
        personalization: itinerary.data?.personalization || '',
        total_days: itinerary.data?.total_days || 0,
        days: itinerary.data?.days || [],
        trip_details: itinerary.data?.trip_details,
        message: 'Itinerary loaded successfully'
      };
    }
    
    throw new Error('Invalid itinerary response format');
  } catch (error) {
    console.error('Failed to fetch itinerary:', error);
    
    if (error instanceof APIError) {
      throw error;
    }
    
    throw new Error('Failed to fetch itinerary details.');
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