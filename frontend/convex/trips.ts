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