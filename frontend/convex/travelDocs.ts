import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getUserDocs = query({
  args: { tripId: v.optional(v.id("trips")) },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    if (args.tripId) {
      return await ctx.db
        .query("travelDocs")
        .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
        .collect();
    }
    
    return await ctx.db
      .query("travelDocs")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .collect();
  },
});

export const getDocsByType = query({
  args: { 
    docType: v.union(v.literal("flight"), v.literal("hotel"), v.literal("visa"), v.literal("passport"), v.literal("insurance"), v.literal("other"))
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
      .query("travelDocs")
      .withIndex("by_type", (q) => q.eq("docType", args.docType))
      .filter((q) => q.eq(q.field("userId"), user._id))
      .collect();
  },
});

export const uploadDocument = mutation({
  args: {
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
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const reminders = [];
    
    // Auto-create reminders based on document type
    if (args.docType === "flight" && args.extractedData?.departureTime) {
      const departureTime = new Date(args.extractedData.departureTime);
      
      reminders.push(
        {
          type: "check_in",
          time: new Date(departureTime.getTime() - 24 * 60 * 60 * 1000).toISOString(),
          sent: false,
        },
        {
          type: "departure_reminder",
          time: new Date(departureTime.getTime() - 3 * 60 * 60 * 1000).toISOString(),
          sent: false,
        }
      );
    }
    
    return await ctx.db.insert("travelDocs", {
      userId: user._id,
      tripId: args.tripId,
      docType: args.docType,
      title: args.title,
      fileUrl: args.fileUrl,
      extractedData: args.extractedData,
      reminders,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const updateDocument = mutation({
  args: {
    docId: v.id("travelDocs"),
    updates: v.object({
      title: v.optional(v.string()),
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
    }),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.patch(args.docId, {
      ...args.updates,
      updatedAt: Date.now(),
    });
  },
});

export const deleteDocument = mutation({
  args: { docId: v.id("travelDocs") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    await ctx.db.delete(args.docId);
  },
});

export const getFlightCheckIns = query({
  args: {},
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    const now = Date.now();
    const next24Hours = now + (24 * 60 * 60 * 1000);
    
    const flightDocs = await ctx.db
      .query("travelDocs")
      .withIndex("by_type", (q) => q.eq("docType", "flight"))
      .filter((q) => q.eq(q.field("userId"), user._id))
      .collect();
    
    return flightDocs
      .filter(doc => {
        const departureTime = doc.extractedData?.departureTime;
        if (!departureTime) return false;
        
        const departure = new Date(departureTime).getTime();
        return departure > now && departure <= next24Hours;
      })
      .map(doc => ({
        ...doc,
        canCheckIn: true,
        checkInWindow: "24 hours before departure",
      }));
  },
});

export const markReminderSent = mutation({
  args: {
    docId: v.id("travelDocs"),
    reminderType: v.string(),
  },
  handler: async (ctx, args) => {
    const doc = await ctx.db.get(args.docId);
    if (!doc) throw new Error("Document not found");
    
    const updatedReminders = doc.reminders?.map(reminder => 
      reminder.type === args.reminderType 
        ? { ...reminder, sent: true }
        : reminder
    ) || [];
    
    await ctx.db.patch(args.docId, {
      reminders: updatedReminders,
      updatedAt: Date.now(),
    });
  },
});