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
  create: (destination, startDate, endDate, travelers, preferences = [], budget = null) =>
    apiCall('planner/smart', {
      method: 'POST',
      body: JSON.stringify({
        destination,
        start_date: startDate,
        end_date: endDate,
        travelers,
        preferences,
        budget
      })
    }),

  updateSlot: (date, slotId, slotData) =>
    apiCall(`planner/slot/${date}/${slotId}`, {
      method: 'PUT',
      body: JSON.stringify(slotData)
    }),

  completeSlot: (slotId) =>
    apiCall('planner/slot/complete', {
      method: 'POST',
      body: JSON.stringify({ slot_id: slotId })
    }),

  save: (itineraryData) =>
    apiCall('save-itinerary', {
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
        seat_class: seatClass
      })
    }),

  getCheapestDates: (origin, destination, departureDate = null, oneWay = false, duration = null) =>
    apiCall('flights/cheapest-dates', {
      params: new URLSearchParams({
        origin,
        destination,
        ...(departureDate && { departure_date: departureDate }),
        one_way: oneWay,
        ...(duration && { duration })
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

// Restaurant Search API
export const restaurants = {
  search: (query, location) =>
    apiCall('restaurants/search', {
      method: 'POST',
      body: JSON.stringify({ query, location })
    })
};

// AI Chat API
export const chat = {
  sendMessage: (message, context = null) =>
    apiCall('chat/agent', {
      method: 'POST',
      body: JSON.stringify({ message, context })
    })
};

// Weather API
export const weather = {
  get: (location, date) =>
    apiCall(`weather/${location}?date=${date}`)
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

// Direct API functions for components
export const createSmartItinerary = (data) => 
  apiCall('planner/smart', { method: 'POST', body: JSON.stringify(data) });

export const saveItinerary = (data) => 
  apiCall('save-itinerary', { method: 'POST', body: JSON.stringify(data) });

export const completeSlot = (slotId) => 
  apiCall('planner/slot/complete', { method: 'POST', body: JSON.stringify({ slot_id: slotId }) });

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