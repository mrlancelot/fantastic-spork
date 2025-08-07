import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Doc } from "./_generated/dataModel";

export const getUserSlots = query({
  args: { 
    date: v.string(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    return await ctx.db
      .query("slots")
      .withIndex("by_user_date", (q) => 
        q.eq("userId", user._id).eq("date", args.date)
      )
      .order("asc")
      .collect();
  },
});

export const getTripSlots = query({
  args: { 
    tripId: v.id("trips"),
    date: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    if (args.date) {
      return await ctx.db
        .query("slots")
        .withIndex("by_trip_date", (q) => 
          q.eq("tripId", args.tripId).eq("date", args.date)
        )
        .order("asc")
        .collect();
    }
    
    return await ctx.db
      .query("slots")
      .filter((q) => q.eq(q.field("tripId"), args.tripId))
      .order("asc")
      .collect();
  },
});

export const createSlot = mutation({
  args: {
    tripId: v.id("trips"),
    date: v.string(),
    slotType: v.union(v.literal("morning"), v.literal("midday"), v.literal("evening"), v.literal("night"), v.literal("custom")),
    title: v.string(),
    description: v.optional(v.string()),
    startTime: v.string(),
    endTime: v.string(),
    color: v.string(),
    theme: v.optional(v.union(v.literal("relax"), v.literal("eat"), v.literal("explore"), v.literal("adventure"))),
    location: v.optional(v.object({
      lat: v.number(),
      lng: v.number(),
      address: v.string(),
      placeId: v.optional(v.string()),
    })),
    budget: v.optional(v.number()),
    packingItems: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const existingSlots = await ctx.db
      .query("slots")
      .withIndex("by_trip_date", (q) => 
        q.eq("tripId", args.tripId).eq("date", args.date)
      )
      .collect();
    
    const slotId = `slot_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return await ctx.db.insert("slots", {
      userId: user._id,
      tripId: args.tripId,
      date: args.date,
      slotId,
      slotType: args.slotType,
      title: args.title,
      description: args.description,
      location: args.location,
      startTime: args.startTime,
      endTime: args.endTime,
      color: args.color,
      theme: args.theme,
      status: "pending",
      budget: args.budget,
      packingItems: args.packingItems,
      order: existingSlots.length,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const updateSlot = mutation({
  args: {
    slotId: v.id("slots"),
    updates: v.object({
      title: v.optional(v.string()),
      description: v.optional(v.string()),
      startTime: v.optional(v.string()),
      endTime: v.optional(v.string()),
      location: v.optional(v.object({
        lat: v.number(),
        lng: v.number(),
        address: v.string(),
        placeId: v.optional(v.string()),
      })),
      theme: v.optional(v.union(v.literal("relax"), v.literal("eat"), v.literal("explore"), v.literal("adventure"))),
      packingItems: v.optional(v.array(v.string())),
      planBOptions: v.optional(v.array(v.object({
        title: v.string(),
        reason: v.string(),
        location: v.optional(v.string()),
      }))),
    }),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.patch(args.slotId, {
      ...args.updates,
      updatedAt: Date.now(),
    });
  },
});

export const completeSlot = mutation({
  args: {
    slotId: v.id("slots"),
    moodRating: v.optional(v.number()),
    energyLevel: v.optional(v.number()),
    actualSpent: v.optional(v.number()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const slot = await ctx.db.get(args.slotId);
    if (!slot) throw new Error("Slot not found");
    
    await ctx.db.patch(args.slotId, {
      status: "completed",
      completedAt: Date.now(),
      moodRating: args.moodRating,
      energyLevel: args.energyLevel,
      actualSpent: args.actualSpent,
      notes: args.notes,
      updatedAt: Date.now(),
    });
    
    // Update journey progress
    const journey = await ctx.db
      .query("journeys")
      .withIndex("by_trip", (q) => q.eq("tripId", slot.tripId))
      .first();
    
    if (journey) {
      const todayProgress = journey.dailyProgress.find(p => p.date === slot.date);
      if (todayProgress) {
        const updatedProgress = journey.dailyProgress.map(p => 
          p.date === slot.date 
            ? { ...p, slotsCompleted: p.slotsCompleted + 1, score: p.score + 100 }
            : p
        );
        await ctx.db.patch(journey._id, {
          dailyProgress: updatedProgress,
          updatedAt: Date.now(),
        });
      }
    }
    
    // Check for achievements
    const user = await ctx.db.get(slot.userId);
    if (user) {
      const totalSlots = await ctx.db
        .query("slots")
        .withIndex("by_user_date", (q) => q.eq("userId", slot.userId).eq("date", slot.date))
        .filter((q) => q.eq(q.field("status"), "completed"))
        .collect();
      
      if (totalSlots.length === 4) {
        // Create "Perfect Day" achievement
        const existingAchievement = await ctx.db
          .query("achievements")
          .withIndex("by_user", (q) => q.eq("userId", slot.userId))
          .filter((q) => q.eq(q.field("type"), "perfect_day"))
          .first();
        
        if (!existingAchievement) {
          await ctx.db.insert("achievements", {
            userId: slot.userId,
            type: "perfect_day",
            name: "Perfect Day",
            description: "Complete all 4 slots in a single day",
            icon: "🏆",
            points: 500,
            tier: "gold",
            progress: 1,
            maxProgress: 1,
            completed: true,
            completedAt: Date.now(),
            category: "completion",
            createdAt: Date.now(),
            updatedAt: Date.now(),
          });
        }
      }
    }
  },
});

export const reorderSlots = mutation({
  args: {
    tripId: v.id("trips"),
    date: v.string(),
    slotIds: v.array(v.id("slots")),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    for (let i = 0; i < args.slotIds.length; i++) {
      await ctx.db.patch(args.slotIds[i], {
        order: i,
        updatedAt: Date.now(),
      });
    }
  },
});

export const deleteSlot = mutation({
  args: {
    slotId: v.id("slots"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.delete(args.slotId);
  },
});

export const checkInSlot = mutation({
  args: {
    slotId: v.id("slots"),
    location: v.object({
      lat: v.number(),
      lng: v.number(),
    }),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.patch(args.slotId, {
      status: "in_progress",
      checkInTime: Date.now(),
      updatedAt: Date.now(),
    });
    
    // Add to group sync if part of a group
    const slot = await ctx.db.get(args.slotId);
    if (slot) {
      const groupSync = await ctx.db
        .query("groupSync")
        .withIndex("by_trip", (q) => q.eq("tripId", slot.tripId))
        .first();
      
      if (groupSync) {
        await ctx.db.patch(groupSync._id, {
          groupCheckIns: [
            ...groupSync.groupCheckIns,
            {
              slotId: args.slotId,
              userId: slot.userId,
              time: Date.now(),
              location: args.location,
            },
          ],
          updatedAt: Date.now(),
        });
      }
    }
  },
});