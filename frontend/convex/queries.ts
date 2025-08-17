import { query } from "./_generated/server";
import { v } from "convex/values";

// Get job by ID
export const getJob = query({
  args: { id: v.id("jobs") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get itinerary by ID
export const getItinerary = query({
  args: { id: v.id("itineraries") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get all activities for an itinerary
export const getActivitiesByItinerary = query({
  args: { itineraryId: v.id("itineraries") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("activities")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();
  },
});

// Get all flights for an itinerary
export const getFlightsByItinerary = query({
  args: { itineraryId: v.id("itineraries") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("flights")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();
  },
});

// Get all hotels for an itinerary
export const getHotelsByItinerary = query({
  args: { itineraryId: v.id("itineraries") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("hotels")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();
  },
});

// Get all restaurants for an itinerary
export const getRestaurantsByItinerary = query({
  args: { itineraryId: v.id("itineraries") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("restaurants")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();
  },
});

// Get complete itinerary data (aggregated)
export const getCompleteItinerary = query({
  args: { itineraryId: v.id("itineraries") },
  handler: async (ctx, args) => {
    const itinerary = await ctx.db.get(args.itineraryId);
    if (!itinerary) {
      return null;
    }

    const activities = await ctx.db
      .query("activities")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();

    const flights = await ctx.db
      .query("flights")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();

    const hotels = await ctx.db
      .query("hotels")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();

    const restaurants = await ctx.db
      .query("restaurants")
      .withIndex("by_itinerary", (q) => q.eq("itineraryId", args.itineraryId))
      .collect();

    return {
      itinerary,
      activities,
      flights,
      hotels,
      restaurants,
    };
  },
});

// Get user itineraries
export const getUserItineraries = query({
  args: { userId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("itineraries")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

// Get user flights
export const getUserFlights = query({
  args: { userId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("flights")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

// Get user hotels
export const getUserHotels = query({
  args: { userId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("hotels")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});