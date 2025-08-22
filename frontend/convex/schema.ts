import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Users table
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    createdAt: v.number(),
    lastLogin: v.optional(v.number()),
  }).index("by_clerk", ["clerkId"]),

  // Itineraries table
  itineraries: defineTable({
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
  }).index("by_user", ["userId"]),

  // Itinerary days table (new)
  itinerary_days: defineTable({
    itineraryId: v.id("itineraries"),
    dayNumber: v.number(),
    date: v.string(),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_itinerary", ["itineraryId"]),

  // Activities table
  activities: defineTable({
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
  }).index("by_itinerary", ["itineraryId"]),

  // Flights table
  flights: defineTable({
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
    class: v.optional(v.string()),
    bookingReference: v.optional(v.string()),
    status: v.optional(v.union(
      v.literal("searching"),
      v.literal("booked"),
      v.literal("cancelled"),
      v.literal("completed")
    )),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_user", ["userId"])
    .index("by_itinerary", ["itineraryId"]),

  // Hotels table
  hotels: defineTable({
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
    bookingReference: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    status: v.optional(v.union(
      v.literal("searching"),
      v.literal("booked"),
      v.literal("cancelled"),
      v.literal("completed")
    )),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_user", ["userId"])
    .index("by_itinerary", ["itineraryId"]),

  // Restaurants table
  restaurants: defineTable({
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
  }).index("by_user", ["userId"])
    .index("by_itinerary", ["itineraryId"]),

  // Jobs table
  jobs: defineTable({
    id: v.optional(v.string()), // String ID for backend reference
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
    scheduledFor: v.optional(v.number()),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_user", ["userId"])
    .index("by_status", ["status"])
    .index("by_string_id", ["id"]),
});