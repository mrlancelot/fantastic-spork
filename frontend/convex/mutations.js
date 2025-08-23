import { mutation } from "./_generated/server";
import { v } from "convex/values";

// ==================== USER MUTATIONS ====================
export const createUser = mutation({
  args: {
    clerkId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    createdAt: v.number(),
    lastLogin: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("users", args);
  },
});

// ==================== ITINERARY MUTATIONS ====================
export const createItinerary = mutation({
  args: {
    userId: v.optional(v.string()),
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    status: v.union(v.literal("draft"), v.literal("published"), v.literal("archived")),
    interests: v.optional(v.array(v.string())),
    budget: v.optional(v.number()),
    data: v.optional(v.any()),
    createdAt: v.number(),
    updatedAt: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("itineraries", args);
  },
});

export const createItineraryDay = mutation({
  args: {
    itineraryId: v.id("itineraries"),
    dayNumber: v.number(),
    date: v.string(),
    createdAt: v.number(),
    updatedAt: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("itinerary_days", args);
  },
});

// ==================== ACTIVITY MUTATIONS ====================
export const createActivity = mutation({
  args: {
    itineraryId: v.id("itineraries"),
    itineraryDayId: v.optional(v.id("itinerary_days")),
    day: v.number(),
    time: v.string(),
    title: v.string(),
    description: v.optional(v.string()),
    location: v.optional(v.string()),
    duration: v.optional(v.number()),
    type: v.optional(v.string()),
    createdAt: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activities", args);
  },
});

// ==================== FLIGHT MUTATIONS ====================
export const createFlight = mutation({
  args: {
    userId: v.optional(v.string()),
    itineraryId: v.optional(v.id("itineraries")),
    origin: v.string(),
    destination: v.string(),
    airline: v.string(),
    flightNumber: v.string(),
    departureDate: v.string(),
    returnDate: v.optional(v.string()),
    price: v.number(),
    currency: v.string(),
    stops: v.optional(v.number()),
    duration: v.optional(v.string()),
    status: v.optional(v.union(
      v.literal("searching"),
      v.literal("booked"),
      v.literal("cancelled"),
      v.literal("completed")
    )),
    createdAt: v.number(),
    updatedAt: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("flights", args);
  },
});

// ==================== HOTEL MUTATIONS ====================
export const createHotel = mutation({
  args: {
    userId: v.optional(v.string()),
    itineraryId: v.optional(v.id("itineraries")),
    name: v.string(),
    address: v.string(),
    city: v.string(),
    country: v.string(),
    checkInDate: v.string(),
    checkOutDate: v.string(),
    price: v.number(),
    currency: v.string(),
    rating: v.optional(v.number()),
    amenities: v.optional(v.array(v.string())),
    roomType: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    status: v.optional(v.union(
      v.literal("searching"),
      v.literal("booked"),
      v.literal("cancelled"),
      v.literal("completed")
    )),
    createdAt: v.number(),
    updatedAt: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("hotels", args);
  },
});

// ==================== RESTAURANT MUTATIONS ====================
export const createRestaurant = mutation({
  args: {
    userId: v.optional(v.string()),
    itineraryId: v.optional(v.id("itineraries")),
    name: v.string(),
    address: v.string(),
    city: v.string(),
    cuisine: v.optional(v.array(v.string())),
    priceRange: v.optional(v.string()),
    rating: v.optional(v.number()),
    phone: v.optional(v.string()),
    website: v.optional(v.string()),
    hours: v.optional(v.string()),
    description: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    reservationDate: v.optional(v.string()),
    reservationTime: v.optional(v.string()),
    partySize: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("restaurants", args);
  },
});

// ==================== JOB MUTATIONS ====================
export const createJob = mutation({
  args: {
    id: v.string(),  // String ID from backend (required for updates)
    type: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    payload: v.optional(v.any()),
    result: v.optional(v.any()),
    error: v.optional(v.string()),
    progress: v.optional(v.number()),
    userId: v.optional(v.string()),
    retryCount: v.optional(v.number()),
    maxRetries: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("jobs", args);
  },
});

export const updateJob = mutation({
  args: {
    job_id: v.string(), // String ID from backend
    status: v.optional(v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    )),
    progress: v.optional(v.number()),
    result: v.optional(v.string()),
    error: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Find job by string ID field (not _id)
    const jobs = await ctx.db
      .query("jobs")
      .withIndex("by_string_id", (q) => q.eq("id", args.job_id))
      .collect();
    
    if (jobs.length === 0) {
      throw new Error(`Job not found: ${args.job_id}`);
    }
    
    const job = jobs[0];
    const updates = {
      updatedAt: Date.now(),
    };
    
    if (args.status !== undefined) {
      updates.status = args.status;
    }
    if (args.progress !== undefined) {
      updates.progress = args.progress;
    }
    if (args.result !== undefined) {
      try {
        updates.result = JSON.parse(args.result);
      } catch {
        updates.result = args.result;
      }
    }
    if (args.error !== undefined) {
      updates.error = args.error;
    }
    
    return await ctx.db.patch(job._id, updates);
  },
});

// ==================== BATCH OPERATIONS ====================
export const createFlightsBatch = mutation({
  args: {
    flights: v.array(v.object({
      userId: v.optional(v.string()),
      itineraryId: v.optional(v.id("itineraries")),
      origin: v.string(),
      destination: v.string(),
      airline: v.string(),
      flightNumber: v.string(),
      departureDate: v.string(),
      returnDate: v.optional(v.string()),
      price: v.number(),
      currency: v.string(),
      stops: v.optional(v.number()),
      duration: v.optional(v.string()),
      status: v.optional(v.union(
        v.literal("searching"),
        v.literal("booked"),
        v.literal("cancelled"),
        v.literal("completed")
      )),
      createdAt: v.number(),
      updatedAt: v.number(),
    })),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const flight of args.flights) {
      const id = await ctx.db.insert("flights", flight);
      ids.push(id);
    }
    return ids;
  },
});

export const createHotelsBatch = mutation({
  args: {
    hotels: v.array(v.object({
      userId: v.optional(v.string()),
      itineraryId: v.optional(v.id("itineraries")),
      name: v.string(),
      address: v.string(),
      city: v.string(),
      country: v.string(),
      checkInDate: v.string(),
      checkOutDate: v.string(),
      price: v.number(),
      currency: v.string(),
      rating: v.optional(v.number()),
      amenities: v.optional(v.array(v.string())),
      roomType: v.optional(v.string()),
      imageUrl: v.optional(v.string()),
      status: v.optional(v.union(
        v.literal("searching"),
        v.literal("booked"),
        v.literal("cancelled"),
        v.literal("completed")
      )),
      createdAt: v.number(),
      updatedAt: v.number(),
    })),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const hotel of args.hotels) {
      const id = await ctx.db.insert("hotels", hotel);
      ids.push(id);
    }
    return ids;
  },
});

export const createRestaurantsBatch = mutation({
  args: {
    restaurants: v.array(v.object({
      userId: v.optional(v.string()),
      itineraryId: v.optional(v.id("itineraries")),
      name: v.string(),
      address: v.string(),
      city: v.string(),
      cuisine: v.optional(v.array(v.string())),
      priceRange: v.optional(v.string()),
      rating: v.optional(v.number()),
      phone: v.optional(v.string()),
      website: v.optional(v.string()),
      hours: v.optional(v.string()),
      description: v.optional(v.string()),
      imageUrl: v.optional(v.string()),
      createdAt: v.number(),
      updatedAt: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const restaurant of args.restaurants) {
      const id = await ctx.db.insert("restaurants", restaurant);
      ids.push(id);
    }
    return ids;
  },
});