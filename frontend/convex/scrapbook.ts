import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getUserScrapbook = query({
  args: { 
    tripId: v.optional(v.id("trips")),
    type: v.optional(v.union(v.literal("photo"), v.literal("journal"), v.literal("video"), v.literal("audio"))),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    let query = ctx.db
      .query("scrapbook")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.tripId) {
      query = query.filter((q) => q.eq(q.field("tripId"), args.tripId));
    }
    
    if (args.type) {
      query = query.filter((q) => q.eq(q.field("type"), args.type));
    }
    
    return await query
      .order("desc")
      .collect();
  },
});

export const getSlotScrapbook = query({
  args: { slotId: v.id("slots") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("scrapbook")
      .withIndex("by_slot", (q) => q.eq("slotId", args.slotId))
      .collect();
  },
});

export const addScrapbookEntry = mutation({
  args: {
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
    isPublic: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const entry = await ctx.db.insert("scrapbook", {
      userId: user._id,
      tripId: args.tripId,
      slotId: args.slotId,
      type: args.type,
      title: args.title,
      content: args.content,
      mediaUrl: args.mediaUrl,
      thumbnailUrl: args.thumbnailUrl,
      location: args.location,
      tags: args.tags || [],
      isPublic: args.isPublic || false,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
    
    // Check for photographer achievement
    if (args.type === "photo") {
      const photoCount = await ctx.db
        .query("scrapbook")
        .withIndex("by_user", (q) => q.eq("userId", user._id))
        .filter((q) => q.eq(q.field("type"), "photo"))
        .collect();
      
      if (photoCount.length === 10) {
        // User just reached 10 photos - unlock photographer achievement
        const achievement = await ctx.db
          .query("achievements")
          .withIndex("by_user", (q) => q.eq("userId", user._id))
          .filter((q) => q.eq(q.field("type"), "photographer"))
          .first();
        
        if (achievement && !achievement.completed) {
          await ctx.db.patch(achievement._id, {
            progress: 10,
            completed: true,
            completedAt: Date.now(),
            updatedAt: Date.now(),
          });
          
          // Update user points
          await ctx.db.patch(user._id, {
            totalPoints: (user.totalPoints || 0) + achievement.points,
            updatedAt: Date.now(),
          });
        }
      }
    }
    
    // Check for writer achievement
    if (args.type === "journal") {
      const journalCount = await ctx.db
        .query("scrapbook")
        .withIndex("by_user", (q) => q.eq("userId", user._id))
        .filter((q) => q.eq(q.field("type"), "journal"))
        .collect();
      
      if (journalCount.length === 5) {
        const achievement = await ctx.db
          .query("achievements")
          .withIndex("by_user", (q) => q.eq("userId", user._id))
          .filter((q) => q.eq(q.field("type"), "writer"))
          .first();
        
        if (achievement && !achievement.completed) {
          await ctx.db.patch(achievement._id, {
            progress: 5,
            completed: true,
            completedAt: Date.now(),
            updatedAt: Date.now(),
          });
          
          await ctx.db.patch(user._id, {
            totalPoints: (user.totalPoints || 0) + achievement.points,
            updatedAt: Date.now(),
          });
        }
      }
    }
    
    return entry;
  },
});

export const updateScrapbookEntry = mutation({
  args: {
    entryId: v.id("scrapbook"),
    updates: v.object({
      title: v.optional(v.string()),
      content: v.optional(v.string()),
      tags: v.optional(v.array(v.string())),
      isPublic: v.optional(v.boolean()),
    }),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.patch(args.entryId, {
      ...args.updates,
      updatedAt: Date.now(),
    });
  },
});

export const deleteScrapbookEntry = mutation({
  args: { entryId: v.id("scrapbook") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.delete(args.entryId);
  },
});

export const getTripPhotoStory = query({
  args: { tripId: v.id("trips") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    // Get all photos for the trip, grouped by day
    const photos = await ctx.db
      .query("scrapbook")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .filter((q) => 
        q.and(
          q.eq(q.field("userId"), user._id),
          q.eq(q.field("type"), "photo")
        )
      )
      .collect();
    
    // Group photos by date
    const photosByDate = photos.reduce((acc, photo) => {
      const date = new Date(photo.createdAt).toISOString().split('T')[0];
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(photo);
      return acc;
    }, {} as Record<string, typeof photos>);
    
    // Sort dates and create story structure
    const sortedDates = Object.keys(photosByDate).sort();
    
    return sortedDates.map(date => ({
      date,
      dayNumber: sortedDates.indexOf(date) + 1,
      photos: photosByDate[date].sort((a, b) => a.createdAt - b.createdAt),
      photoCount: photosByDate[date].length,
    }));
  },
});

export const getPublicScrapbook = query({
  args: { 
    tripId: v.optional(v.id("trips")),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    let query = ctx.db
      .query("scrapbook")
      .filter((q) => q.eq(q.field("isPublic"), true));
    
    if (args.tripId) {
      query = query.filter((q) => q.eq(q.field("tripId"), args.tripId));
    }
    
    const results = await query
      .order("desc")
      .collect();
    
    if (args.limit) {
      return results.slice(0, args.limit);
    }
    
    return results;
  },
});

export const searchScrapbook = query({
  args: { 
    searchTerm: v.string(),
    tripId: v.optional(v.id("trips")),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    let query = ctx.db
      .query("scrapbook")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.tripId) {
      query = query.filter((q) => q.eq(q.field("tripId"), args.tripId));
    }
    
    const entries = await query.collect();
    
    const searchTermLower = args.searchTerm.toLowerCase();
    
    return entries.filter(entry => 
      (entry.title && entry.title.toLowerCase().includes(searchTermLower)) ||
      entry.content.toLowerCase().includes(searchTermLower) ||
      (entry.tags && entry.tags.some(tag => tag.toLowerCase().includes(searchTermLower))) ||
      (entry.location && entry.location.name.toLowerCase().includes(searchTermLower))
    );
  },
});

export const generateAutoJournal = mutation({
  args: {
    tripId: v.id("trips"),
    slotId: v.id("slots"),
    activities: v.array(v.string()),
    mood: v.optional(v.string()),
    weather: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const slot = await ctx.db.get(args.slotId);
    if (!slot) throw new Error("Slot not found");
    
    // Generate auto journal entry based on activities and mood
    let journalContent = `Today I explored ${slot.title}. `;
    
    if (args.activities.length > 0) {
      journalContent += `The highlights included ${args.activities.join(', ')}. `;
    }
    
    if (args.mood) {
      const moodTexts = {
        excited: "I felt absolutely thrilled throughout the experience!",
        happy: "It was a wonderful and enjoyable time.",
        neutral: "It was a decent experience overall.",
        tired: "I was feeling a bit tired, but it was still worthwhile.",
        stressed: "It was a bit overwhelming, but I'm glad I did it.",
      };
      journalContent += moodTexts[args.mood as keyof typeof moodTexts] || "";
    }
    
    if (args.weather) {
      journalContent += ` The weather was ${args.weather}, which added to the atmosphere.`;
    }
    
    journalContent += " This will definitely be a memorable part of my trip!";
    
    return await ctx.db.insert("scrapbook", {
      userId: user._id,
      tripId: args.tripId,
      slotId: args.slotId,
      type: "journal",
      title: `${slot.title} - Auto Journal`,
      content: journalContent,
      tags: ["auto-generated", slot.theme || "travel"],
      isPublic: false,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});