import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const create = mutation({
  args: {
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    budget: v.optional(v.number()),
    travelers: v.number(),
    activities: v.array(v.string()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user) {
      throw new Error("User not found");
    }

    const tripId = await ctx.db.insert("trips", {
      userId: user._id,
      destination: args.destination,
      startDate: args.startDate,
      endDate: args.endDate,
      budget: args.budget,
      travelers: args.travelers,
      activities: args.activities,
      notes: args.notes,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });

    return tripId;
  },
});

export const getUserTrips = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return [];
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user) {
      return [];
    }

    const trips = await ctx.db
      .query("trips")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .order("desc")
      .collect();

    return trips;
  },
});

export const getTrip = query({
  args: { id: v.id("trips") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null;
    }

    const trip = await ctx.db.get(args.id);
    if (!trip) {
      return null;
    }

    // Verify the user owns this trip
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user || trip.userId !== user._id) {
      return null;
    }

    return trip;
  },
});

export const updateTrip = mutation({
  args: {
    id: v.id("trips"),
    destination: v.optional(v.string()),
    startDate: v.optional(v.string()),
    endDate: v.optional(v.string()),
    budget: v.optional(v.number()),
    travelers: v.optional(v.number()),
    activities: v.optional(v.array(v.string())),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const trip = await ctx.db.get(args.id);
    if (!trip) {
      throw new Error("Trip not found");
    }

    // Verify the user owns this trip
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user || trip.userId !== user._id) {
      throw new Error("Unauthorized");
    }

    const { id, ...updates } = args;
    await ctx.db.patch(args.id, {
      ...updates,
      updatedAt: Date.now(),
    });
  },
});

export const deleteTrip = mutation({
  args: { id: v.id("trips") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const trip = await ctx.db.get(args.id);
    if (!trip) {
      throw new Error("Trip not found");
    }

    // Verify the user owns this trip
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user || trip.userId !== user._id) {
      throw new Error("Unauthorized");
    }

    // Delete associated itineraries
    const itineraries = await ctx.db
      .query("itineraries")
      .withIndex("by_trip", (q) => q.eq("tripId", args.id))
      .collect();
    
    for (const itinerary of itineraries) {
      await ctx.db.delete(itinerary._id);
    }

    // Delete associated chats
    const chats = await ctx.db
      .query("chats")
      .withIndex("by_trip", (q) => q.eq("tripId", args.id))
      .collect();
    
    for (const chat of chats) {
      await ctx.db.delete(chat._id);
    }

    // Delete the trip
    await ctx.db.delete(args.id);
  },
});

export const createWithFullItinerary = mutation({
  args: {
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    travelers: v.number(),
    departureCities: v.array(v.string()),
    tripType: v.optional(v.string()),
    itineraryData: v.any(), // Full itinerary with booking options
    bookingValidation: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user) {
      throw new Error("User not found");
    }

    const tripId = await ctx.db.insert("trips", {
      userId: user._id,
      destination: args.destination,
      startDate: args.startDate,
      endDate: args.endDate,
      travelers: args.travelers,
      departureCities: args.departureCities,
      tripType: args.tripType || "group travel",
      activities: [], // Extract from itinerary if needed
      itineraryData: args.itineraryData,
      bookingValidation: args.bookingValidation,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });

    return tripId;
  },
});

export const createFromBackend = mutation({
  args: {
    destination: v.string(),
    dates: v.string(),
    travelers: v.number(),
    departureCities: v.array(v.string()),
    tripType: v.optional(v.string()),
    itineraryData: v.any(),
    bookingValidation: v.optional(v.any()),
    userId: v.string(), // Clerk user ID
  },
  handler: async (ctx, args) => {
    // Find user by Clerk ID
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", args.userId))
      .unique();
    
    if (!user) {
      throw new Error("User not found");
    }

    // Parse dates if they're in range format
    let startDate = args.dates;
    let endDate = args.dates;
    
    if (args.dates.includes(" to ")) {
      const [start, end] = args.dates.split(" to ");
      startDate = start.trim();
      endDate = end.trim();
    }

    // Extract activities from itinerary data
    const activities: string[] = [];
    const itinerary = args.itineraryData;
    
    // Extract activity names from the activities section
    if (itinerary?.activities && Array.isArray(itinerary.activities)) {
      for (const activity of itinerary.activities) {
        if (activity?.name) {
          activities.push(activity.name);
        }
      }
    }
    
    // If no activities found, add placeholder activities from schedule
    if (activities.length === 0 && itinerary?.schedule) {
      Object.values(itinerary.schedule).forEach((dayActivities: any) => {
        if (Array.isArray(dayActivities)) {
          activities.push(...dayActivities);
        }
      });
    }
    
    // Ensure we have at least one activity (required by schema)
    if (activities.length === 0) {
      activities.push("Exploring " + args.destination);
    }

    const tripId = await ctx.db.insert("trips", {
      userId: user._id,
      destination: args.destination,
      startDate,
      endDate,
      travelers: args.travelers,
      departureCities: args.departureCities,
      tripType: args.tripType || "group travel",
      activities,
      itineraryData: args.itineraryData,
      bookingValidation: args.bookingValidation,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });

    return tripId;
  },
});