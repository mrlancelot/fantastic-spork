// API service for itinerary creation
const API_BASE_URL = 'http://localhost:8000';

export interface ItineraryRequest {
  trip_type: 'round_trip' | 'one_way';
  from_city: string;
  to_city: string;
  departure_date: string;
  return_date?: string;
  adults: number;
  travel_class: 'economy' | 'business' | 'first';
  interests: string;
  price_range: 'budget' | 'mid_range' | 'upscale';
}

export interface Activity {
  time: string;
  title: string;
  description: string;
  location: string;
  duration: string | null;
  activity_type: 'flight' | 'hotel' | 'meal' | 'activity';
  additional_info: string | null;
}

export interface Day {
  day_number: number;
  date: string;
  year: number;
  activities: Activity[];
}

export interface ItineraryResponse {
  status: string;
  title: string;
  personalization: string;
  total_days: number;
  days: Day[];
  trip_details?: any;
  message?: string;
}

export interface JobStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  result?: any;
}

export class ApiService {
  static async createItinerary(request: ItineraryRequest): Promise<ItineraryResponse> {
    const response = await fetch(`${API_BASE_URL}/itinerary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  static async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/status`);
    
    if (!response.ok) {
      throw new Error(`Failed to get job status: ${response.status}`);
    }

    return response.json();
  }

  // Helper to poll job status until completion
  static async pollJobStatus(
    jobId: string, 
    onProgress?: (progress: number) => void,
    maxAttempts: number = 60, // 5 minutes with 5s intervals
    interval: number = 5000
  ): Promise<JobStatus> {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const status = await this.getJobStatus(jobId);
        
        if (onProgress) {
          onProgress(status.progress);
        }
        
        if (status.status === 'completed') {
          return status;
        }
        
        if (status.status === 'failed') {
          throw new Error(status.error || 'Job failed');
        }
        
        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, interval));
        attempts++;
        
      } catch (error) {
        if (attempts >= maxAttempts - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, interval));
        attempts++;
      }
    }
    
    throw new Error('Job polling timeout - itinerary creation took too long');
  }
}
