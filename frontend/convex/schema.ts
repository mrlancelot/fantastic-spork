import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    emailVerified: v.optional(v.boolean()),
    name: v.optional(v.string()),
    firstName: v.optional(v.string()),
    lastName: v.optional(v.string()),
    username: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    hasImage: v.optional(v.boolean()),
    phoneNumber: v.optional(v.string()),
    phoneVerified: v.optional(v.boolean()),
    twoFactorEnabled: v.optional(v.boolean()),
    externalId: v.optional(v.string()),
    lastSignInAt: v.optional(v.string()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_clerk_id", ["clerkId"])
    .index("by_email", ["email"])
    .index("by_username", ["username"]),
  
  trips: defineTable({
    userId: v.id("users"),
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    budget: v.optional(v.number()),
    travelers: v.number(),
    activities: v.array(v.string()),
    notes: v.optional(v.string()),
    // Enhanced fields for booking support
    itineraryData: v.optional(v.any()), // Store the full itinerary with booking options
    bookingValidation: v.optional(v.any()), // Store booking validation status
    departureCities: v.optional(v.array(v.string())),
    tripType: v.optional(v.string()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_date", ["startDate"]),
  
  itineraries: defineTable({
    tripId: v.id("trips"),
    userId: v.id("users"),
    day: v.number(),
    activities: v.array(v.object({
      time: v.string(),
      title: v.string(),
      description: v.string(),
      location: v.optional(v.string()),
      duration: v.optional(v.number()),
    })),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_trip", ["tripId"])
    .index("by_trip_day", ["tripId", "day"]),
  
  chats: defineTable({
    userId: v.id("users"),
    tripId: v.optional(v.id("trips")),
    messages: v.array(v.object({
      role: v.union(v.literal("user"), v.literal("assistant")),
      content: v.string(),
      timestamp: v.number(),
    })),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_trip", ["tripId"]),
});