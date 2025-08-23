// Convex mutation for creating flights
// This should be deployed to your Convex project

import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create_flight = mutation({
  args: {
    // Match the Python model fields
    id: v.string(),
    itinerary_id: v.optional(v.string()),
    origin: v.string(),
    destination: v.string(),
    airline: v.string(),
    flight_number: v.optional(v.string()),
    departure_date: v.string(),
    arrival_date: v.optional(v.string()),
    price: v.number(),
    stops: v.number(),
    duration: v.optional(v.string()),
    booking_url: v.optional(v.string()),
    created_at: v.string(),
  },
  handler: async (ctx, args) => {
    // Map Python fields to Convex schema
    const flightData = {
      userId: "system", // Default system user
      origin: args.origin,
      destination: args.destination,
      airline: args.airline,
      flightNumber: args.flight_number || "",
      departureDate: args.departure_date,
      returnDate: args.arrival_date,
      price: args.price,
      stops: args.stops || 0,
      duration: args.duration || "",
      currency: "USD",
      status: "searching" as const,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    // If itinerary_id is provided, we need to convert it to Convex ID format
    // For now, we'll skip this linkage
    
    const id = await ctx.db.insert("flights", flightData);
    return id;
  },
});