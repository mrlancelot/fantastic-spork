import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Doc } from "./_generated/dataModel";

// Save or update a rich itinerary from the backend
export const saveFromBackend = mutation({
  args: {
    userId: v.id("users"),
    itineraryData: v.object({
      itineraryId: v.string(),
      destination: v.string(),
      startDate: v.string(),
      endDate: v.string(),
      durationDays: v.number(),
      travelers: v.number(),
      totalBudget: v.number(),
      interests: v.array(v.string()),
      pace: v.string(),
      dailyPlans: v.array(v.any()),
      recommendations: v.object({
        flights: v.array(v.any()),
        hotels: v.array(v.any()),
        restaurants: v.array(v.any()),
        activities: v.array(v.any()),
      }),
      aiAnalysis: v.string(),
      exportFormat: v.object({
        version: v.string(),
        type: v.string(),
        exportable: v.boolean(),
      }),
      journeyData: v.object({
        totalActivities: v.number(),
        completed: v.number(),
        progressPercentage: v.number(),
        levels: v.number(),
        currentLevel: v.number(),
        badges: v.array(v.any()),
      }),
    }),
  },
  handler: async (ctx, args) => {
    const { userId, itineraryData } = args;
    const now = Date.now();
    
    // Check if itinerary already exists
    const existing = await ctx.db
      .query("richItineraries")
      .withIndex("by_itinerary_id", (q) => q.eq("itineraryId", itineraryData.itineraryId))
      .first();
    
    if (existing) {
      // Update existing itinerary
      await ctx.db.patch(existing._id, {
        ...itineraryData,
        updatedAt: now,
        lastAccessedAt: now,
      });
      return existing._id;
    } else {
      // Deactivate any currently active itineraries for this user
      const activeItineraries = await ctx.db
        .query("richItineraries")
        .withIndex("by_active", (q) => q.eq("userId", userId).eq("isActive", true))
        .collect();
      
      for (const activeItinerary of activeItineraries) {
        await ctx.db.patch(activeItinerary._id, { isActive: false });
      }
      
      // Create new itinerary
      const itineraryId = await ctx.db.insert("richItineraries", {
        userId,
        ...itineraryData,
        createdAt: now,
        updatedAt: now,
        lastAccessedAt: now,
        isActive: true,
        isShared: false,
      });
      
      return itineraryId;
    }
  },
});

// Get the active itinerary for a user
export const getActiveItinerary = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    const itinerary = await ctx.db
      .query("richItineraries")
      .withIndex("by_active", (q) => q.eq("userId", args.userId).eq("isActive", true))
      .first();
    
    // Note: Cannot update lastAccessedAt in a query - queries are read-only
    // This could be moved to a separate mutation if needed
    
    return itinerary;
  },
});

// Get all itineraries for a user
export const getUserItineraries = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    const itineraries = await ctx.db
      .query("richItineraries")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .collect();
    
    return itineraries;
  },
});

// Get itinerary by external ID
export const getByItineraryId = query({
  args: { itineraryId: v.string() },
  handler: async (ctx, args) => {
    const itinerary = await ctx.db
      .query("richItineraries")
      .withIndex("by_itinerary_id", (q) => q.eq("itineraryId", args.itineraryId))
      .first();
    
    // Note: Cannot update lastAccessedAt in a query - queries are read-only
    // This could be moved to a separate mutation if needed
    
    return itinerary;
  },
});

// Update slot completion status
export const updateSlotCompletion = mutation({
  args: {
    itineraryId: v.string(),
    dayIndex: v.number(),
    slotIndex: v.number(),
    completed: v.boolean(),
  },
  handler: async (ctx, args) => {
    const itinerary = await ctx.db
      .query("richItineraries")
      .withIndex("by_itinerary_id", (q) => q.eq("itineraryId", args.itineraryId))
      .first();
    
    if (!itinerary) {
      throw new Error("Itinerary not found");
    }
    
    // Update the specific slot
    const updatedDailyPlans = [...itinerary.dailyPlans];
    if (updatedDailyPlans[args.dayIndex] && updatedDailyPlans[args.dayIndex].slots[args.slotIndex]) {
      updatedDailyPlans[args.dayIndex].slots[args.slotIndex].completed = args.completed;
    }
    
    // Update journey data
    const totalCompleted = updatedDailyPlans.reduce((total, day) => {
      return total + day.slots.filter((slot: any) => slot.completed).length;
    }, 0);
    
    const journeyData = {
      ...itinerary.journeyData,
      completed: totalCompleted,
      progressPercentage: Math.round((totalCompleted / itinerary.journeyData.totalActivities) * 100),
      currentLevel: Math.min(Math.floor(totalCompleted / 4) + 1, itinerary.journeyData.levels),
    };
    
    // Update badges based on progress
    const badges = [...itinerary.journeyData.badges];
    if (totalCompleted >= 3) {
      const explorerBadge = badges.find((b: any) => b.id === "explorer");
      if (explorerBadge) explorerBadge.unlocked = true;
    }
    if (totalCompleted >= 6) {
      const foodieBadge = badges.find((b: any) => b.id === "foodie");
      if (foodieBadge) foodieBadge.unlocked = true;
    }
    if (totalCompleted >= 10) {
      const adventurerBadge = badges.find((b: any) => b.id === "adventurer");
      if (adventurerBadge) adventurerBadge.unlocked = true;
    }
    journeyData.badges = badges;
    
    // Save updates
    await ctx.db.patch(itinerary._id, {
      dailyPlans: updatedDailyPlans,
      journeyData,
      updatedAt: Date.now(),
    });
    
    return { success: true, journeyData };
  },
});

// Set an itinerary as active
export const setActiveItinerary = mutation({
  args: {
    userId: v.id("users"),
    itineraryId: v.string(),
  },
  handler: async (ctx, args) => {
    // Deactivate all user's itineraries
    const userItineraries = await ctx.db
      .query("richItineraries")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
    
    for (const itinerary of userItineraries) {
      if (itinerary.itineraryId === args.itineraryId) {
        await ctx.db.patch(itinerary._id, { 
          isActive: true,
          lastAccessedAt: Date.now(),
        });
      } else if (itinerary.isActive) {
        await ctx.db.patch(itinerary._id, { isActive: false });
      }
    }
    
    return { success: true };
  },
});

// Delete an itinerary
export const deleteItinerary = mutation({
  args: {
    itineraryId: v.string(),
    userId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const itinerary = await ctx.db
      .query("richItineraries")
      .withIndex("by_itinerary_id", (q) => q.eq("itineraryId", args.itineraryId))
      .first();
    
    if (!itinerary || itinerary.userId !== args.userId) {
      throw new Error("Itinerary not found or access denied");
    }
    
    await ctx.db.delete(itinerary._id);
    return { success: true };
  },
});