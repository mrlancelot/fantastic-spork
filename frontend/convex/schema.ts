import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  activities: defineTable({
    createdAt: v.float64(),
    day: v.float64(),
    description: v.optional(v.string()),
    duration: v.optional(v.float64()),
    itineraryId: v.id("itineraries"),
    location: v.optional(v.string()),
    time: v.string(),
    title: v.string(),
    type: v.optional(v.string()),
  }).index("by_itinerary", ["itineraryId"]),
  
  flights: defineTable({
    airline: v.string(),
    bookingReference: v.optional(v.string()),
    class: v.optional(v.string()),
    createdAt: v.float64(),
    currency: v.string(),
    departureDate: v.string(),
    destination: v.string(),
    duration: v.optional(v.string()),
    flightNumber: v.string(),
    itineraryId: v.optional(v.id("itineraries")),
    origin: v.string(),
    price: v.float64(),
    returnDate: v.optional(v.string()),
    status: v.optional(
      v.union(
        v.literal("searching"),
        v.literal("booked"),
        v.literal("cancelled"),
        v.literal("completed")
      )
    ),
    stops: v.optional(v.float64()),
    updatedAt: v.float64(),
    userId: v.string(),
  })
    .index("by_itinerary", ["itineraryId"])
    .index("by_user", ["userId"]),
  
  hotels: defineTable({
    address: v.string(),
    amenities: v.optional(v.array(v.string())),
    bookingReference: v.optional(v.string()),
    checkInDate: v.string(),
    checkOutDate: v.string(),
    city: v.string(),
    country: v.string(),
    createdAt: v.float64(),
    currency: v.string(),
    imageUrl: v.optional(v.string()),
    itineraryId: v.optional(v.id("itineraries")),
    name: v.string(),
    price: v.float64(),
    rating: v.optional(v.float64()),
    roomType: v.optional(v.string()),
    status: v.optional(
      v.union(
        v.literal("searching"),
        v.literal("booked"),
        v.literal("cancelled"),
        v.literal("completed")
      )
    ),
    updatedAt: v.float64(),
    userId: v.string(),
  })
    .index("by_itinerary", ["itineraryId"])
    .index("by_user", ["userId"]),
  
  itineraries: defineTable({
    budget: v.optional(v.float64()),
    createdAt: v.float64(),
    data: v.optional(v.any()),
    destination: v.string(),
    endDate: v.string(),
    interests: v.optional(v.array(v.string())),
    startDate: v.string(),
    status: v.union(
      v.literal("draft"),
      v.literal("published"),
      v.literal("archived")
    ),
    updatedAt: v.float64(),
    userId: v.string(),
  }).index("by_user", ["userId"]),
  
  jobs: defineTable({
    completedAt: v.optional(v.float64()),
    createdAt: v.float64(),
    error: v.optional(v.string()),
    maxRetries: v.optional(v.float64()),
    payload: v.optional(v.any()),
    result: v.optional(v.any()),
    retryCount: v.optional(v.float64()),
    scheduledFor: v.optional(v.float64()),
    startedAt: v.optional(v.float64()),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    type: v.string(),
    updatedAt: v.float64(),
    userId: v.optional(v.string()),
  })
    .index("by_status", ["status"])
    .index("by_type", ["type"])
    .index("by_user", ["userId"]),
  
  restaurants: defineTable({
    address: v.string(),
    city: v.string(),
    createdAt: v.float64(),
    cuisine: v.optional(v.array(v.string())),
    description: v.optional(v.string()),
    hours: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    itineraryId: v.optional(v.id("itineraries")),
    name: v.string(),
    partySize: v.optional(v.float64()),
    phone: v.optional(v.string()),
    priceRange: v.optional(v.string()),
    rating: v.optional(v.float64()),
    reservationDate: v.optional(v.string()),
    reservationTime: v.optional(v.string()),
    updatedAt: v.optional(v.float64()),
    userId: v.optional(v.string()),
    website: v.optional(v.string()),
  })
    .index("by_itinerary", ["itineraryId"])
    .index("by_user", ["userId"]),
  
  users: defineTable({
    clerkId: v.string(),
    createdAt: v.float64(),
    email: v.string(),
    lastLogin: v.optional(v.float64()),
    name: v.optional(v.string()),
  }).index("by_clerk", ["clerkId"]),
});