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
    level: v.optional(v.number()),
    totalPoints: v.optional(v.number()),
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
  
  // New comprehensive itinerary table for master agent data
  richItineraries: defineTable({
    userId: v.id("users"),
    itineraryId: v.string(), // External ID from backend
    destination: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    durationDays: v.number(),
    travelers: v.number(),
    totalBudget: v.number(),
    interests: v.array(v.string()),
    pace: v.string(),
    
    // Daily plans with time slots
    dailyPlans: v.array(v.object({
      day: v.number(),
      date: v.string(),
      dayName: v.string(),
      slots: v.array(v.object({
        id: v.string(),
        timeSlot: v.string(),
        startTime: v.string(),
        endTime: v.string(),
        title: v.string(),
        description: v.string(),
        location: v.string(),
        type: v.string(),
        budget: v.number(),
        completed: v.optional(v.boolean()),
        restaurant: v.optional(v.any()),
        recommendations: v.optional(v.array(v.any())),
        activity: v.optional(v.string()),      // For display compatibility
        duration: v.optional(v.string()),      // Time duration info
        booking_url: v.optional(v.string()),   // Restaurant booking links
      })),
      weather: v.optional(v.any()),
    })),
    
    // Recommendations from master agent
    recommendations: v.object({
      flights: v.array(v.any()),
      hotels: v.array(v.any()),
      restaurants: v.array(v.any()),
      activities: v.array(v.any()),
    }),
    
    // AI analysis and insights
    aiAnalysis: v.string(),
    
    // Export metadata
    exportFormat: v.object({
      version: v.string(),
      type: v.string(),
      exportable: v.boolean(),
    }),
    
    // Journey gamification data
    journeyData: v.object({
      totalActivities: v.number(),
      completed: v.number(),
      progressPercentage: v.number(),
      levels: v.number(),
      currentLevel: v.number(),
      badges: v.array(v.object({
        id: v.string(),
        name: v.string(),
        icon: v.string(),
        unlocked: v.boolean(),
      })),
    }),
    
    // Metadata
    createdAt: v.number(),
    updatedAt: v.number(),
    lastAccessedAt: v.number(),
    isActive: v.boolean(), // Currently active itinerary
    isShared: v.boolean(), // Shared with other users
    sharedWith: v.optional(v.array(v.id("users"))),
  })
    .index("by_user", ["userId"])
    .index("by_itinerary_id", ["itineraryId"])
    .index("by_active", ["userId", "isActive"])
    .index("by_dates", ["startDate", "endDate"])
    .index("by_destination", ["destination"]),
  
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
  
  slots: defineTable({
    userId: v.id("users"),
    tripId: v.id("trips"),
    date: v.string(),
    slotId: v.string(),
    slotType: v.union(v.literal("morning"), v.literal("midday"), v.literal("evening"), v.literal("night"), v.literal("custom")),
    title: v.string(),
    description: v.optional(v.string()),
    location: v.optional(v.object({
      lat: v.number(),
      lng: v.number(),
      address: v.string(),
      placeId: v.optional(v.string()),
    })),
    startTime: v.string(),
    endTime: v.string(),
    color: v.string(),
    theme: v.optional(v.union(v.literal("relax"), v.literal("eat"), v.literal("explore"), v.literal("adventure"))),
    status: v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed"), v.literal("skipped")),
    completedAt: v.optional(v.number()),
    checkInTime: v.optional(v.number()),
    budget: v.optional(v.number()),
    actualSpent: v.optional(v.number()),
    packingItems: v.optional(v.array(v.string())),
    weatherAlert: v.optional(v.string()),
    planBOptions: v.optional(v.array(v.object({
      title: v.string(),
      reason: v.string(),
      location: v.optional(v.string()),
    }))),
    moodRating: v.optional(v.number()),
    energyLevel: v.optional(v.number()),
    photos: v.optional(v.array(v.string())),
    notes: v.optional(v.string()),
    order: v.number(),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user_date", ["userId", "date"])
    .index("by_trip_date", ["tripId", "date"])
    .index("by_status", ["status"]),
  
  journeys: defineTable({
    userId: v.id("users"),
    tripId: v.id("trips"),
    currentLevel: v.number(),
    totalLevels: v.number(),
    mapTheme: v.string(),
    characterPosition: v.object({
      x: v.number(),
      y: v.number(),
      levelProgress: v.number(),
    }),
    unlockedBadges: v.array(v.object({
      id: v.string(),
      name: v.string(),
      icon: v.string(),
      unlockedAt: v.number(),
    })),
    dailyProgress: v.array(v.object({
      date: v.string(),
      slotsCompleted: v.number(),
      totalSlots: v.number(),
      distanceWalked: v.number(),
      score: v.number(),
    })),
    animations: v.optional(v.array(v.string())),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_trip", ["tripId"]),
  
  travelDocs: defineTable({
    userId: v.id("users"),
    tripId: v.optional(v.id("trips")),
    docType: v.union(v.literal("flight"), v.literal("hotel"), v.literal("visa"), v.literal("passport"), v.literal("insurance"), v.literal("other")),
    title: v.string(),
    fileUrl: v.string(),
    extractedData: v.optional(v.object({
      pnr: v.optional(v.string()),
      flightNumber: v.optional(v.string()),
      airline: v.optional(v.string()),
      seat: v.optional(v.string()),
      terminal: v.optional(v.string()),
      gate: v.optional(v.string()),
      departureTime: v.optional(v.string()),
      checkInUrl: v.optional(v.string()),
    })),
    reminders: v.optional(v.array(v.object({
      type: v.string(),
      time: v.string(),
      sent: v.boolean(),
    }))),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_trip", ["tripId"])
    .index("by_type", ["docType"]),
  
  groupSync: defineTable({
    tripId: v.id("trips"),
    groupId: v.string(),
    members: v.array(v.object({
      userId: v.id("users"),
      role: v.union(v.literal("leader"), v.literal("member")),
      joinedAt: v.number(),
    })),
    sharedSlots: v.array(v.id("slots")),
    groupCheckIns: v.array(v.object({
      slotId: v.id("slots"),
      userId: v.id("users"),
      time: v.number(),
      location: v.object({
        lat: v.number(),
        lng: v.number(),
      }),
    })),
    sharedAchievements: v.array(v.object({
      type: v.string(),
      earnedAt: v.number(),
      earnedBy: v.array(v.id("users")),
    })),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_trip", ["tripId"])
    .index("by_group", ["groupId"]),
  
  achievements: defineTable({
    userId: v.id("users"),
    type: v.string(),
    name: v.string(),
    description: v.string(),
    icon: v.string(),
    points: v.number(),
    tier: v.union(v.literal("bronze"), v.literal("silver"), v.literal("gold"), v.literal("platinum")),
    progress: v.number(),
    maxProgress: v.number(),
    completed: v.boolean(),
    completedAt: v.optional(v.number()),
    category: v.union(v.literal("exploration"), v.literal("social"), v.literal("completion"), v.literal("special")),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_type", ["type"])
    .index("by_completed", ["completed"]),
  
  moodTracking: defineTable({
    userId: v.id("users"),
    slotId: v.id("slots"),
    tripId: v.id("trips"),
    mood: v.union(v.literal("excited"), v.literal("happy"), v.literal("neutral"), v.literal("tired"), v.literal("stressed")),
    energyLevel: v.number(),
    feedback: v.optional(v.string()),
    weatherImpact: v.optional(v.boolean()),
    crowdImpact: v.optional(v.boolean()),
    suggestions: v.optional(v.array(v.string())),
    timestamp: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_slot", ["slotId"])
    .index("by_trip", ["tripId"]),
  
  scrapbook: defineTable({
    userId: v.id("users"),
    tripId: v.id("trips"),
    slotId: v.optional(v.id("slots")),
    type: v.union(v.literal("photo"), v.literal("journal"), v.literal("video"), v.literal("audio")),
    title: v.optional(v.string()),
    content: v.string(),
    mediaUrl: v.optional(v.string()),
    thumbnailUrl: v.optional(v.string()),
    location: v.optional(v.object({
      lat: v.number(),
      lng: v.number(),
      name: v.string(),
    })),
    tags: v.optional(v.array(v.string())),
    isPublic: v.boolean(),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_trip", ["tripId"])
    .index("by_slot", ["slotId"]),
  
  searchCache: defineTable({
    cacheKey: v.string(),
    searchType: v.union(v.literal("flight"), v.literal("hotel"), v.literal("activity"), v.literal("restaurant")),
    query: v.object({
      origin: v.optional(v.string()),
      destination: v.optional(v.string()),
      startDate: v.optional(v.string()),
      endDate: v.optional(v.string()),
      adults: v.optional(v.number()),
      params: v.optional(v.any()),
    }),
    results: v.any(),
    ttl: v.number(),
    createdAt: v.number(),
    expiresAt: v.number(),
  })
    .index("by_key", ["cacheKey"])
    .index("by_type", ["searchType"])
    .index("by_expiry", ["expiresAt"]),
});