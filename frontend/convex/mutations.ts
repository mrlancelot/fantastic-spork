import { mutation } from "./_generated/server";
import { v } from "convex/values";

// Itineraries mutations
export const createItinerary = mutation({
  args: {
    userId: v.string(),
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    budget: v.optional(v.float64()),
    interests: v.optional(v.array(v.string())),
    status: v.union(v.literal("draft"), v.literal("published"), v.literal("archived")),
    data: v.optional(v.any()),
    createdAt: v.float64(),
    updatedAt: v.float64(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("itineraries", args);
  },
});

// Activities mutations
export const createActivity = mutation({
  args: {
    itineraryId: v.id("itineraries"),
    day: v.float64(),
    time: v.string(),
    title: v.string(),
    description: v.optional(v.string()),
    location: v.optional(v.string()),
    duration: v.optional(v.float64()),
    type: v.optional(v.string()),
    createdAt: v.float64(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activities", args);
  },
});

// Flights mutations
export const createFlight = mutation({
  args: {
    itineraryId: v.optional(v.id("itineraries")),
    userId: v.string(),
    origin: v.string(),
    destination: v.string(),
    departureDate: v.string(),
    returnDate: v.optional(v.string()),
    airline: v.string(),
    flightNumber: v.string(),
    price: v.float64(),
    currency: v.string(),
    duration: v.optional(v.string()),
    class: v.optional(v.string()),
    stops: v.optional(v.float64()),
    bookingReference: v.optional(v.string()),
    status: v.optional(v.union(v.literal("searching"), v.literal("booked"), v.literal("cancelled"), v.literal("completed"))),
    createdAt: v.float64(),
    updatedAt: v.float64(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("flights", args);
  },
});

// Hotels mutations
export const createHotel = mutation({
  args: {
    itineraryId: v.optional(v.id("itineraries")),
    userId: v.string(),
    name: v.string(),
    address: v.string(),
    city: v.string(),
    country: v.string(),
    checkInDate: v.string(),
    checkOutDate: v.string(),
    price: v.float64(),
    currency: v.string(),
    rating: v.optional(v.float64()),
    amenities: v.optional(v.array(v.string())),
    roomType: v.optional(v.string()),
    bookingReference: v.optional(v.string()),
    status: v.optional(v.union(v.literal("searching"), v.literal("booked"), v.literal("cancelled"), v.literal("completed"))),
    imageUrl: v.optional(v.string()),
    createdAt: v.float64(),
    updatedAt: v.float64(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("hotels", args);
  },
});

// Restaurants mutations
export const createRestaurant = mutation({
  args: {
    itineraryId: v.optional(v.id("itineraries")),
    userId: v.optional(v.string()),
    name: v.string(),
    address: v.string(),
    city: v.string(),
    cuisine: v.optional(v.array(v.string())),
    priceRange: v.optional(v.string()),
    rating: v.optional(v.float64()),
    phone: v.optional(v.string()),
    website: v.optional(v.string()),
    hours: v.optional(v.string()),
    reservationDate: v.optional(v.string()),
    reservationTime: v.optional(v.string()),
    partySize: v.optional(v.float64()),
    imageUrl: v.optional(v.string()),
    description: v.optional(v.string()),
    createdAt: v.float64(),
    updatedAt: v.optional(v.float64()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("restaurants", args);
  },
});

// Jobs mutations
export const createJob = mutation({
  args: {
    type: v.string(),
    status: v.union(v.literal("pending"), v.literal("processing"), v.literal("completed"), v.literal("failed")),
    userId: v.optional(v.string()),
    payload: v.optional(v.any()),
    result: v.optional(v.any()),
    error: v.optional(v.string()),
    retryCount: v.optional(v.float64()),
    maxRetries: v.optional(v.float64()),
    scheduledFor: v.optional(v.float64()),
    startedAt: v.optional(v.float64()),
    completedAt: v.optional(v.float64()),
    createdAt: v.float64(),
    updatedAt: v.float64(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("jobs", args);
  },
});

export const updateJob = mutation({
  args: {
    id: v.id("jobs"),
    updates: v.object({
      status: v.optional(v.union(v.literal("pending"), v.literal("processing"), v.literal("completed"), v.literal("failed"))),
      result: v.optional(v.any()),
      error: v.optional(v.string()),
      retryCount: v.optional(v.float64()),
      startedAt: v.optional(v.float64()),
      completedAt: v.optional(v.float64()),
      updatedAt: v.float64(),
    }),
  },
  handler: async (ctx, args) => {
    const { id, updates } = args;
    return await ctx.db.patch(id, updates);
  },
});

// Users mutations
export const createUser = mutation({
  args: {
    clerkId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    createdAt: v.float64(),
    lastLogin: v.optional(v.float64()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("users", args);
  },
});