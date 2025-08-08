import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getJourney = query({
  args: { tripId: v.id("trips") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return null;
    
    return await ctx.db
      .query("journeys")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
  },
});

export const getUserJourney = query({
  args: {},
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return null;
    
    return await ctx.db
      .query("journeys")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .first();
  },
});

export const createJourney = mutation({
  args: {
    tripId: v.id("trips"),
    totalLevels: v.optional(v.number()),
    mapTheme: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    return await ctx.db.insert("journeys", {
      userId: user._id,
      tripId: args.tripId,
      currentLevel: 1,
      totalLevels: args.totalLevels || 5,
      mapTheme: args.mapTheme || "tropical",
      characterPosition: { x: 10, y: 80, levelProgress: 0 },
      unlockedBadges: [],
      dailyProgress: [],
      animations: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const updateProgress = mutation({
  args: {
    tripId: v.id("trips"),
    date: v.string(),
    slotsCompleted: v.number(),
    totalSlots: v.number(),
    distanceWalked: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const journey = await ctx.db
      .query("journeys")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
    
    if (!journey) throw new Error("Journey not found");
    
    const score = args.slotsCompleted * 100;
    const progressPercent = (args.slotsCompleted / args.totalSlots) * 100;
    
    // Update daily progress
    const existingProgress = journey.dailyProgress.find(p => p.date === args.date);
    let updatedDailyProgress;
    
    if (existingProgress) {
      updatedDailyProgress = journey.dailyProgress.map(p => 
        p.date === args.date 
          ? { ...p, slotsCompleted: args.slotsCompleted, score, distanceWalked: args.distanceWalked || 0 }
          : p
      );
    } else {
      updatedDailyProgress = [
        ...journey.dailyProgress,
        {
          date: args.date,
          slotsCompleted: args.slotsCompleted,
          totalSlots: args.totalSlots,
          distanceWalked: args.distanceWalked || 0,
          score,
        }
      ];
    }
    
    // Update character position based on progress
    const newLevel = Math.min(
      journey.totalLevels, 
      Math.floor(progressPercent / 20) + 1
    );
    
    const characterPosition = {
      x: Math.min(90, 10 + (progressPercent * 0.8)),
      y: 80 - (newLevel - 1) * 15,
      levelProgress: progressPercent % 20,
    };
    
    // Check for new badges
    const newBadges = [];
    if (args.slotsCompleted === args.totalSlots && !journey.unlockedBadges.find(b => b.id === "perfect_day")) {
      newBadges.push({
        id: "perfect_day",
        name: "Perfect Day",
        icon: "🏆",
        unlockedAt: Date.now(),
      });
    }
    
    if (args.distanceWalked && args.distanceWalked > 10000 && !journey.unlockedBadges.find(b => b.id === "walker")) {
      newBadges.push({
        id: "walker",
        name: "Walker",
        icon: "🚶‍♀️",
        unlockedAt: Date.now(),
      });
    }
    
    await ctx.db.patch(journey._id, {
      currentLevel: newLevel,
      characterPosition,
      dailyProgress: updatedDailyProgress,
      unlockedBadges: [...journey.unlockedBadges, ...newBadges],
      updatedAt: Date.now(),
    });
    
    return {
      newLevel: newLevel > journey.currentLevel,
      newBadges,
      characterPosition,
    };
  },
});

export const unlockBadge = mutation({
  args: {
    tripId: v.id("trips"),
    badgeId: v.string(),
    badgeName: v.string(),
    badgeIcon: v.string(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const journey = await ctx.db
      .query("journeys")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
    
    if (!journey) throw new Error("Journey not found");
    
    const alreadyUnlocked = journey.unlockedBadges.find(b => b.id === args.badgeId);
    if (alreadyUnlocked) return false;
    
    const newBadge = {
      id: args.badgeId,
      name: args.badgeName,
      icon: args.badgeIcon,
      unlockedAt: Date.now(),
    };
    
    await ctx.db.patch(journey._id, {
      unlockedBadges: [...journey.unlockedBadges, newBadge],
      updatedAt: Date.now(),
    });
    
    return newBadge;
  },
});