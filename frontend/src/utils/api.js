// API client for TravelAI MVP backend
const API_BASE = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : '';

class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}/api/${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new APIError(
        error.detail || error.error || `HTTP ${response.status}`,
        response.status,
        error
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new APIError(`Network error: ${error.message}`, 0, { originalError: error });
  }
}

// Smart Daily Planner API
export const smartPlanner = {
  create: (destination, startDate, endDate, travelers = 1, interests = [], budget = 1000) =>
    apiCall('planner/smart', {
      method: 'POST',
      body: JSON.stringify({
        destination,
        start_date: startDate,
        end_date: endDate,
        travelers: travelers || 1,
        interests: interests || [],
        budget: budget || 1000,
        pace: 'moderate'
      })
    }),

  // Slot management - to be implemented in backend
  updateSlot: async (date, slotId, slotData) => {
    console.warn('Slot update API not yet implemented');
    return { status: 'success', message: 'Feature coming soon' };
  },

  completeSlot: async (slotId) => {
    console.warn('Slot complete API not yet implemented');
    return { status: 'success', message: 'Feature coming soon' };
  },

  save: (itineraryData) =>
    apiCall('planner/save', {
      method: 'POST',
      body: JSON.stringify(itineraryData)
    })
};

// Flight Search API
export const flights = {
  search: (origin, destination, departureDate, returnDate = null, adults = 1, seatClass = 'economy') =>
    apiCall('flights/search', {
      method: 'POST',
      body: JSON.stringify({
        origin,
        destination,
        departure_date: departureDate,
        return_date: returnDate,
        adults,
        travel_class: seatClass.toUpperCase(),
        max_results: 10
      })
    }),

  getCheapestDates: (origin, destination) =>
    apiCall('flights/cheapest-dates', {
      method: 'POST',
      body: JSON.stringify({ origin, destination })
    }),

  getFlexible: (origin, destination, departureMonth, tripLengthDays = 7, adults = 1) =>
    apiCall('flights/flexible', {
      method: 'POST',
      body: JSON.stringify({
        origin,
        destination,
        departure_month: departureMonth,
        trip_length_days: tripLengthDays,
        adults
      })
    })
};

// Hotel Search API
export const hotels = {
  search: (cityCode = null, latitude = null, longitude = null, checkInDate, checkOutDate, adults = 1, rooms = 1) =>
    apiCall('hotels/search', {
      method: 'POST',
      body: JSON.stringify({
        city_code: cityCode,
        latitude,
        longitude,
        check_in_date: checkInDate,
        check_out_date: checkOutDate,
        adults,
        rooms
      })
    }),

  getSentiments: (hotelIds) =>
    apiCall(`hotels/sentiments?hotel_ids=${hotelIds.join(',')}`)
};

// Activities API
export const activities = {
  search: (latitude, longitude, radius = 5, adults = 1) =>
    apiCall('activities/search', {
      method: 'POST',
      body: JSON.stringify({
        latitude,
        longitude,
        radius,
        adults
      })
    })
};

// Restaurant Search API - Not yet implemented
export const restaurants = {
  search: async (query, location) => {
    console.warn('Restaurant search API not yet implemented');
    return { 
      status: 'success', 
      restaurants: [],
      message: 'Restaurant search coming soon' 
    };
  }
};

// AI Chat API
export const chat = {
  sendMessage: (message, context = null) =>
    apiCall('chat/agent', {
      method: 'POST',
      body: JSON.stringify({ message, context })
    })
};

// Weather API - Not yet implemented
export const weather = {
  get: async (location, date) => {
    console.warn('Weather API not yet implemented');
    return {
      status: 'success',
      temperature: 72,
      condition: 'Partly Cloudy',
      message: 'Weather data coming soon'
    };
  }
};

// User Management API
export const user = {
  store: (clerkUserId, email, name = null, imageUrl = null) =>
    apiCall('store-user', {
      method: 'POST',
      body: JSON.stringify({
        clerk_user_id: clerkUserId,
        email,
        name,
        image_url: imageUrl
      })
    })
};

// Analytics API
export const analytics = {
  getFlightInspiration: (origin, maxPrice) =>
    apiCall(`analytics/flight-inspiration?origin=${origin}${maxPrice ? `&max_price=${maxPrice}` : ''}`),
  
  getAirportRoutes: (airportCode) =>
    apiCall(`analytics/airport-routes?airport_code=${airportCode}`),
  
  analyzePrices: (origin, destination, departureDate) =>
    apiCall('analytics/price-analysis', {
      method: 'POST',
      body: JSON.stringify({
        origin,
        destination,
        departure_date: departureDate
      })
    })
};

// Direct API functions for components
export const createSmartItinerary = (data) => 
  apiCall('planner/smart', { method: 'POST', body: JSON.stringify(data) });

export const saveItinerary = (data) => 
  apiCall('planner/save', { method: 'POST', body: JSON.stringify(data) });

export const completeSlot = async (slotId) => {
  console.warn('Slot complete API not yet implemented');
  return { status: 'success', message: 'Feature coming soon' };
};

export const searchFlights = (data) => 
  apiCall('flights/search', { method: 'POST', body: JSON.stringify(data) });

export const searchHotels = (data) => 
  apiCall('hotels/search', { method: 'POST', body: JSON.stringify(data) });

export const searchActivities = (data) => 
  apiCall('activities/search', { method: 'POST', body: JSON.stringify(data) });

export const sendChatMessage = (message, context = null) => 
  apiCall('chat/agent', { method: 'POST', body: JSON.stringify({ message, context }) });

// Utility functions
export const api = {
  smartPlanner,
  flights,
  hotels,
  activities,
  restaurants,
  chat,
  weather,
  user,
  analytics,
  // Direct functions
  createSmartItinerary,
  saveItinerary,
  completeSlot,
  searchFlights,
  searchHotels,
  searchActivities,
  sendChatMessage
};

// Health check
export const healthCheck = () => apiCall('health');

export default api;