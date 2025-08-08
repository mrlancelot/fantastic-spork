import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getUserAchievements = query({
  args: { completed: v.optional(v.boolean()) },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    let query = ctx.db
      .query("achievements")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.completed !== undefined) {
      query = query.filter((q) => q.eq(q.field("completed"), args.completed));
    }
    
    return await query.collect();
  },
});

export const getAchievementsByCategory = query({
  args: { 
    category: v.union(v.literal("exploration"), v.literal("social"), v.literal("completion"), v.literal("special"))
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
      .query("achievements")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .filter((q) => q.eq(q.field("category"), args.category))
      .collect();
  },
});

export const createAchievement = mutation({
  args: {
    type: v.string(),
    name: v.string(),
    description: v.string(),
    icon: v.string(),
    points: v.number(),
    tier: v.union(v.literal("bronze"), v.literal("silver"), v.literal("gold"), v.literal("platinum")),
    category: v.union(v.literal("exploration"), v.literal("social"), v.literal("completion"), v.literal("special")),
    maxProgress: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    // Check if achievement already exists
    const existing = await ctx.db
      .query("achievements")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .filter((q) => q.eq(q.field("type"), args.type))
      .first();
    
    if (existing) return existing._id;
    
    return await ctx.db.insert("achievements", {
      userId: user._id,
      type: args.type,
      name: args.name,
      description: args.description,
      icon: args.icon,
      points: args.points,
      tier: args.tier,
      progress: 0,
      maxProgress: args.maxProgress || 1,
      completed: false,
      category: args.category,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const updateProgress = mutation({
  args: {
    achievementId: v.id("achievements"),
    progress: v.number(),
  },
  handler: async (ctx, args) => {
    const achievement = await ctx.db.get(args.achievementId);
    if (!achievement) throw new Error("Achievement not found");
    
    const newProgress = Math.min(args.progress, achievement.maxProgress);
    const completed = newProgress >= achievement.maxProgress;
    const justCompleted = completed && !achievement.completed;
    
    await ctx.db.patch(args.achievementId, {
      progress: newProgress,
      completed,
      completedAt: justCompleted ? Date.now() : achievement.completedAt,
      updatedAt: Date.now(),
    });
    
    // Update user total points if just completed
    if (justCompleted) {
      const user = await ctx.db.get(achievement.userId);
      if (user) {
        await ctx.db.patch(user._id, {
          totalPoints: (user.totalPoints || 0) + achievement.points,
          updatedAt: Date.now(),
        });
      }
    }
    
    return { justCompleted, points: achievement.points };
  },
});

export const completeAchievement = mutation({
  args: {
    type: v.string(),
    earnedPoints: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const achievement = await ctx.db
      .query("achievements")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .filter((q) => q.eq(q.field("type"), args.type))
      .first();
    
    if (!achievement) throw new Error("Achievement not found");
    if (achievement.completed) return achievement;
    
    await ctx.db.patch(achievement._id, {
      progress: achievement.maxProgress,
      completed: true,
      completedAt: Date.now(),
      updatedAt: Date.now(),
    });
    
    // Update user points and level
    const pointsEarned = args.earnedPoints || achievement.points;
    const newTotalPoints = (user.totalPoints || 0) + pointsEarned;
    const newLevel = Math.floor(newTotalPoints / 1000) + 1;
    
    await ctx.db.patch(user._id, {
      totalPoints: newTotalPoints,
      level: newLevel,
      updatedAt: Date.now(),
    });
    
    return {
      ...achievement,
      progress: achievement.maxProgress,
      completed: true,
      completedAt: Date.now(),
      pointsEarned,
      newLevel: newLevel > (user.level || 1),
    };
  },
});

export const initializeUserAchievements = mutation({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    // Check if achievements already initialized
    const existing = await ctx.db
      .query("achievements")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .first();
    
    if (existing) return;
    
    // Initialize basic achievements
    const baseAchievements = [
      {
        type: "first_slot",
        name: "First Steps",
        description: "Complete your first activity slot",
        icon: "👣",
        points: 100,
        tier: "bronze" as const,
        category: "completion" as const,
      },
      {
        type: "perfect_day",
        name: "Perfect Day",
        description: "Complete all 4 slots in a single day",
        icon: "🏆",
        points: 500,
        tier: "gold" as const,
        category: "completion" as const,
      },
      {
        type: "early_bird",
        name: "Early Bird",
        description: "Complete a morning slot before 8 AM",
        icon: "🌅",
        points: 200,
        tier: "silver" as const,
        category: "exploration" as const,
      },
      {
        type: "night_owl",
        name: "Night Owl",
        description: "Complete a night slot after 10 PM",
        icon: "🦉",
        points: 200,
        tier: "silver" as const,
        category: "exploration" as const,
      },
      {
        type: "social_butterfly",
        name: "Social Butterfly",
        description: "Join a group trip",
        icon: "🦋",
        points: 300,
        tier: "silver" as const,
        category: "social" as const,
      },
      {
        type: "explorer",
        name: "Explorer",
        description: "Complete activities in 5 different locations",
        icon: "🗺️",
        points: 1000,
        tier: "gold" as const,
        category: "exploration" as const,
        maxProgress: 5,
      },
      {
        type: "photographer",
        name: "Photographer",
        description: "Add 10 photos to your scrapbook",
        icon: "📸",
        points: 400,
        tier: "silver" as const,
        category: "special" as const,
        maxProgress: 10,
      },
      {
        type: "writer",
        name: "Travel Writer",
        description: "Write 5 journal entries",
        icon: "✍️",
        points: 350,
        tier: "silver" as const,
        category: "special" as const,
        maxProgress: 5,
      },
    ];
    
    const achievementPromises = baseAchievements.map(achievement => 
      ctx.db.insert("achievements", {
        userId: user._id,
        ...achievement,
        progress: 0,
        maxProgress: achievement.maxProgress || 1,
        completed: false,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      })
    );
    
    await Promise.all(achievementPromises);
  },
});

export const getUserStats = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return null;
    
    const achievements = await ctx.db
      .query("achievements")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
    
    const completed = achievements.filter(a => a.completed).length;
    const totalPoints = achievements
      .filter(a => a.completed)
      .reduce((sum, a) => sum + a.points, 0);
    
    const byTier = achievements.reduce((acc, a) => {
      if (a.completed) {
        acc[a.tier] = (acc[a.tier] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);
    
    return {
      level: user.level || 1,
      totalPoints: user.totalPoints || 0,
      totalAchievements: achievements.length,
      completedAchievements: completed,
      completionRate: achievements.length > 0 ? (completed / achievements.length) * 100 : 0,
      byTier,
      nextLevelPoints: ((user.level || 1) * 1000) - (user.totalPoints || 0),
    };
  },
});