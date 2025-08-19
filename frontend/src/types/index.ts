export interface ItineraryDay {
  date: Date;
  activities: Activity[];
}

export interface Activity {
  id: string;
  time: string;
  title: string;
  description: string;
  location: string;
  type: 'sightseeing' | 'restaurant' | 'hotel' | 'transport' | 'activity';
  duration: string;
  cost?: number;
  imageUrl?: string;
}

export interface Itinerary {
  id: string;
  destination: string;
  startDate: Date;
  endDate: Date;
  totalCost: number;
  travelers: number;
  days: ItineraryDay[];
}

export interface ProgressStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  current: boolean;
}