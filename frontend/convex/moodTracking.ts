import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const trackMood = mutation({
  args: {
    slotId: v.id("slots"),
    tripId: v.id("trips"),
    mood: v.union(v.literal("excited"), v.literal("happy"), v.literal("neutral"), v.literal("tired"), v.literal("stressed")),
    energyLevel: v.number(),
    feedback: v.optional(v.string()),
    weatherImpact: v.optional(v.boolean()),
    crowdImpact: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    // Generate AI suggestions based on mood and energy
    const suggestions = [];
    
    if (args.mood === "tired" || args.energyLevel < 4) {
      suggestions.push("Consider a relaxing activity like a spa or quiet cafe");
      suggestions.push("Maybe skip high-energy activities for today");
      suggestions.push("Try a scenic walk or gentle sightseeing");
    } else if (args.mood === "excited" && args.energyLevel > 7) {
      suggestions.push("Perfect time for adventure activities!");
      suggestions.push("Consider extending your exploration time");
      suggestions.push("Try something new and challenging");
    } else if (args.mood === "stressed") {
      suggestions.push("Take some time to decompress");
      suggestions.push("Visit a park or quiet location");
      suggestions.push("Consider mindful activities like art galleries");
    }
    
    if (args.weatherImpact) {
      suggestions.push("Weather might be affecting your mood - consider indoor alternatives");
    }
    
    if (args.crowdImpact) {
      suggestions.push("Try less crowded alternatives or visit during off-peak hours");
    }
    
    return await ctx.db.insert("moodTracking", {
      userId: user._id,
      slotId: args.slotId,
      tripId: args.tripId,
      mood: args.mood,
      energyLevel: args.energyLevel,
      feedback: args.feedback,
      weatherImpact: args.weatherImpact,
      crowdImpact: args.crowdImpact,
      suggestions,
      timestamp: Date.now(),
    });
  },
});

export const getMoodHistory = query({
  args: { 
    tripId: v.optional(v.id("trips")),
    days: v.optional(v.number()),
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
      .query("moodTracking")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.tripId) {
      query = query.filter((q) => q.eq(q.field("tripId"), args.tripId));
    }
    
    const results = await query
      .order("desc")
      .collect();
    
    if (args.days) {
      const cutoff = Date.now() - (args.days * 24 * 60 * 60 * 1000);
      return results.filter(mood => mood.timestamp > cutoff);
    }
    
    return results;
  },
});

export const getMoodAnalytics = query({
  args: { tripId: v.optional(v.id("trips")) },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return null;
    
    let query = ctx.db
      .query("moodTracking")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.tripId) {
      query = query.filter((q) => q.eq(q.field("tripId"), args.tripId));
    }
    
    const moods = await query.collect();
    
    if (moods.length === 0) {
      return {
        averageEnergy: 5,
        moodDistribution: {},
        totalEntries: 0,
        trends: {},
        recommendations: [],
      };
    }
    
    const averageEnergy = moods.reduce((sum, mood) => sum + mood.energyLevel, 0) / moods.length;
    
    const moodDistribution = moods.reduce((acc, mood) => {
      acc[mood.mood] = (acc[mood.mood] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const weatherImpactCount = moods.filter(m => m.weatherImpact).length;
    const crowdImpactCount = moods.filter(m => m.crowdImpact).length;
    
    // Generate recommendations based on patterns
    const recommendations = [];
    
    const dominantMood = Object.entries(moodDistribution)
      .sort(([,a], [,b]) => b - a)[0]?.[0];
    
    if (dominantMood === "tired") {
      recommendations.push("Consider scheduling more rest time between activities");
      recommendations.push("Try shorter, less intensive activities");
    } else if (dominantMood === "stressed") {
      recommendations.push("Build in buffer time between activities");
      recommendations.push("Consider relaxing activities like spas or nature walks");
    } else if (dominantMood === "excited") {
      recommendations.push("You're having a great trip! Consider more adventurous activities");
    }
    
    if (weatherImpactCount > moods.length * 0.3) {
      recommendations.push("Weather seems to affect your mood - plan indoor alternatives");
    }
    
    if (crowdImpactCount > moods.length * 0.3) {
      recommendations.push("Crowds affect your experience - try visiting popular spots during off-peak hours");
    }
    
    return {
      averageEnergy: Math.round(averageEnergy * 10) / 10,
      moodDistribution,
      totalEntries: moods.length,
      trends: {
        weatherImpact: weatherImpactCount / moods.length,
        crowdImpact: crowdImpactCount / moods.length,
        dominantMood,
      },
      recommendations,
    };
  },
});

export const getTripMoodSummary = query({
  args: { tripId: v.id("trips") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return null;
    
    const moods = await ctx.db
      .query("moodTracking")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .filter((q) => q.eq(q.field("userId"), user._id))
      .collect();
    
    if (moods.length === 0) return null;
    
    const dailyMoods = moods.reduce((acc, mood) => {
      const date = new Date(mood.timestamp).toISOString().split('T')[0];
      if (!acc[date]) {
        acc[date] = { moods: [], totalEnergy: 0, count: 0 };
      }
      acc[date].moods.push(mood.mood);
      acc[date].totalEnergy += mood.energyLevel;
      acc[date].count += 1;
      return acc;
    }, {} as Record<string, { moods: string[], totalEnergy: number, count: number }>);
    
    const dailySummary = Object.entries(dailyMoods).map(([date, data]) => ({
      date,
      averageEnergy: data.totalEnergy / data.count,
      dominantMood: data.moods.sort((a, b) => 
        data.moods.filter(m => m === b).length - data.moods.filter(m => m === a).length
      )[0],
      moodCount: data.count,
    }));
    
    const overallAverageEnergy = moods.reduce((sum, mood) => sum + mood.energyLevel, 0) / moods.length;
    
    const bestDay = dailySummary.reduce((best, day) => 
      day.averageEnergy > best.averageEnergy ? day : best
    );
    
    const worstDay = dailySummary.reduce((worst, day) => 
      day.averageEnergy < worst.averageEnergy ? day : worst
    );
    
    return {
      dailySummary,
      overallAverageEnergy: Math.round(overallAverageEnergy * 10) / 10,
      totalEntries: moods.length,
      bestDay,
      worstDay,
      tripDuration: dailySummary.length,
    };
  },
});

export const getSlotMood = query({
  args: { slotId: v.id("slots") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("moodTracking")
      .withIndex("by_slot", (q) => q.eq("slotId", args.slotId))
      .first();
  },
});