import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getCachedResults = query({
  args: { cacheKey: v.string() },
  handler: async (ctx, args) => {
    const cached = await ctx.db
      .query("searchCache")
      .withIndex("by_key", (q) => q.eq("cacheKey", args.cacheKey))
      .first();
    
    if (!cached) return null;
    
    // Check if cache is still valid
    if (Date.now() > cached.expiresAt) {
      // Cache expired, delete it
      await ctx.db.delete(cached._id);
      return null;
    }
    
    return {
      results: cached.results,
      cachedAt: cached.createdAt,
      expiresAt: cached.expiresAt,
    };
  },
});

export const cacheResults = mutation({
  args: {
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
    ttl: v.optional(v.number()), // Time to live in seconds
  },
  handler: async (ctx, args) => {
    // Generate cache key from search parameters
    const keyData = {
      type: args.searchType,
      ...args.query,
    };
    const cacheKey = Buffer.from(JSON.stringify(keyData)).toString('base64');
    
    const ttlMs = (args.ttl || 3600) * 1000; // Default 1 hour
    const expiresAt = Date.now() + ttlMs;
    
    // Check if cache already exists
    const existing = await ctx.db
      .query("searchCache")
      .withIndex("by_key", (q) => q.eq("cacheKey", cacheKey))
      .first();
    
    if (existing) {
      // Update existing cache
      await ctx.db.patch(existing._id, {
        results: args.results,
        expiresAt,
        createdAt: Date.now(),
      });
      return cacheKey;
    }
    
    // Create new cache entry
    await ctx.db.insert("searchCache", {
      cacheKey,
      searchType: args.searchType,
      query: args.query,
      results: args.results,
      ttl: args.ttl || 3600,
      createdAt: Date.now(),
      expiresAt,
    });
    
    return cacheKey;
  },
});

export const generateCacheKey = query({
  args: {
    searchType: v.union(v.literal("flight"), v.literal("hotel"), v.literal("activity"), v.literal("restaurant")),
    params: v.any(),
  },
  handler: async (ctx, args) => {
    const keyData = {
      type: args.searchType,
      ...args.params,
    };
    return Buffer.from(JSON.stringify(keyData)).toString('base64');
  },
});

export const clearExpiredCache = mutation({
  args: {},
  handler: async (ctx) => {
    const now = Date.now();
    const expired = await ctx.db
      .query("searchCache")
      .withIndex("by_expiry", (q) => q.lt("expiresAt", now))
      .collect();
    
    const deletePromises = expired.map(cache => ctx.db.delete(cache._id));
    await Promise.all(deletePromises);
    
    return expired.length;
  },
});

export const getCacheStats = query({
  args: { searchType: v.optional(v.union(v.literal("flight"), v.literal("hotel"), v.literal("activity"), v.literal("restaurant"))) },
  handler: async (ctx, args) => {
    let query = ctx.db.query("searchCache");
    
    if (args.searchType) {
      query = query.withIndex("by_type", (q) => q.eq("searchType", args.searchType));
    }
    
    const caches = await query.collect();
    const now = Date.now();
    
    const stats = {
      total: caches.length,
      valid: caches.filter(c => c.expiresAt > now).length,
      expired: caches.filter(c => c.expiresAt <= now).length,
      byType: {} as Record<string, number>,
      averageTtl: 0,
      oldestCache: null as Date | null,
      newestCache: null as Date | null,
    };
    
    if (caches.length > 0) {
      // Count by type
      caches.forEach(cache => {
        stats.byType[cache.searchType] = (stats.byType[cache.searchType] || 0) + 1;
      });
      
      // Calculate average TTL
      stats.averageTtl = caches.reduce((sum, cache) => sum + cache.ttl, 0) / caches.length;
      
      // Find oldest and newest
      const timestamps = caches.map(c => c.createdAt);
      stats.oldestCache = new Date(Math.min(...timestamps));
      stats.newestCache = new Date(Math.max(...timestamps));
    }
    
    return stats;
  },
});

export const invalidateCache = mutation({
  args: {
    searchType: v.optional(v.union(v.literal("flight"), v.literal("hotel"), v.literal("activity"), v.literal("restaurant"))),
    destination: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let caches = await ctx.db.query("searchCache").collect();
    
    // Filter caches to invalidate
    if (args.searchType) {
      caches = caches.filter(cache => cache.searchType === args.searchType);
    }
    
    if (args.destination) {
      caches = caches.filter(cache => 
        cache.query.destination === args.destination || 
        cache.query.origin === args.destination
      );
    }
    
    const deletePromises = caches.map(cache => ctx.db.delete(cache._id));
    await Promise.all(deletePromises);
    
    return caches.length;
  },
});

export const preloadCache = mutation({
  args: {
    searchType: v.union(v.literal("flight"), v.literal("hotel"), v.literal("activity"), v.literal("restaurant")),
    destinations: v.array(v.string()),
    baseDate: v.string(),
  },
  handler: async (ctx, args) => {
    // This would typically trigger background jobs to preload popular searches
    // For now, we'll just create placeholder cache entries that can be populated
    
    const preloadPromises = args.destinations.map(async (destination) => {
      const cacheKey = Buffer.from(JSON.stringify({
        type: args.searchType,
        destination,
        date: args.baseDate,
        preload: true,
      })).toString('base64');
      
      const existing = await ctx.db
        .query("searchCache")
        .withIndex("by_key", (q) => q.eq("cacheKey", cacheKey))
        .first();
      
      if (!existing) {
        await ctx.db.insert("searchCache", {
          cacheKey,
          searchType: args.searchType,
          query: {
            destination,
            startDate: args.baseDate,
            params: { preload: true },
          },
          results: { placeholder: true, needsData: true },
          ttl: 7200, // 2 hours for preloaded data
          createdAt: Date.now(),
          expiresAt: Date.now() + (2 * 60 * 60 * 1000),
        });
      }
    });
    
    await Promise.all(preloadPromises);
    return args.destinations.length;
  },
});