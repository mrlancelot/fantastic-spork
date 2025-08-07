import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getGroupSync = query({
  args: { tripId: v.id("trips") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("groupSync")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
  },
});

export const getUserGroups = query({
  args: {},
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return [];
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) return [];
    
    const allGroups = await ctx.db.query("groupSync").collect();
    
    return allGroups.filter(group => 
      group.members.some(member => member.userId === user._id)
    );
  },
});

export const createGroupSync = mutation({
  args: {
    tripId: v.id("trips"),
    groupId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const groupId = args.groupId || `group_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return await ctx.db.insert("groupSync", {
      tripId: args.tripId,
      groupId,
      members: [{
        userId: user._id,
        role: "leader",
        joinedAt: Date.now(),
      }],
      sharedSlots: [],
      groupCheckIns: [],
      sharedAchievements: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const joinGroup = mutation({
  args: {
    groupId: v.string(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const groupSync = await ctx.db
      .query("groupSync")
      .withIndex("by_group", (q) => q.eq("groupId", args.groupId))
      .first();
    
    if (!groupSync) throw new Error("Group not found");
    
    // Check if user is already a member
    const existingMember = groupSync.members.find(member => member.userId === user._id);
    if (existingMember) return groupSync._id;
    
    const updatedMembers = [
      ...groupSync.members,
      {
        userId: user._id,
        role: "member" as const,
        joinedAt: Date.now(),
      }
    ];
    
    await ctx.db.patch(groupSync._id, {
      members: updatedMembers,
      updatedAt: Date.now(),
    });
    
    return groupSync._id;
  },
});

export const shareSlot = mutation({
  args: {
    tripId: v.id("trips"),
    slotId: v.id("slots"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const groupSync = await ctx.db
      .query("groupSync")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
    
    if (!groupSync) throw new Error("Group not found");
    
    if (!groupSync.sharedSlots.includes(args.slotId)) {
      await ctx.db.patch(groupSync._id, {
        sharedSlots: [...groupSync.sharedSlots, args.slotId],
        updatedAt: Date.now(),
      });
    }
  },
});

export const addGroupCheckIn = mutation({
  args: {
    tripId: v.id("trips"),
    slotId: v.id("slots"),
    location: v.object({
      lat: v.number(),
      lng: v.number(),
    }),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const groupSync = await ctx.db
      .query("groupSync")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
    
    if (!groupSync) return; // No group sync for this trip
    
    const newCheckIn = {
      slotId: args.slotId,
      userId: user._id,
      time: Date.now(),
      location: args.location,
    };
    
    await ctx.db.patch(groupSync._id, {
      groupCheckIns: [...groupSync.groupCheckIns, newCheckIn],
      updatedAt: Date.now(),
    });
  },
});

export const addSharedAchievement = mutation({
  args: {
    tripId: v.id("trips"),
    achievementType: v.string(),
    earnedBy: v.array(v.id("users")),
  },
  handler: async (ctx, args) => {
    const groupSync = await ctx.db
      .query("groupSync")
      .withIndex("by_trip", (q) => q.eq("tripId", args.tripId))
      .first();
    
    if (!groupSync) return;
    
    const sharedAchievement = {
      type: args.achievementType,
      earnedAt: Date.now(),
      earnedBy: args.earnedBy,
    };
    
    await ctx.db.patch(groupSync._id, {
      sharedAchievements: [...groupSync.sharedAchievements, sharedAchievement],
      updatedAt: Date.now(),
    });
  },
});

export const getGroupMembers = query({
  args: { groupId: v.string() },
  handler: async (ctx, args) => {
    const groupSync = await ctx.db
      .query("groupSync")
      .withIndex("by_group", (q) => q.eq("groupId", args.groupId))
      .first();
    
    if (!groupSync) return [];
    
    const members = [];
    for (const member of groupSync.members) {
      const user = await ctx.db.get(member.userId);
      if (user) {
        members.push({
          ...user,
          role: member.role,
          joinedAt: member.joinedAt,
        });
      }
    }
    
    return members;
  },
});

export const leaveGroup = mutation({
  args: { groupId: v.string() },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .first();
    
    if (!user) throw new Error("User not found");
    
    const groupSync = await ctx.db
      .query("groupSync")
      .withIndex("by_group", (q) => q.eq("groupId", args.groupId))
      .first();
    
    if (!groupSync) throw new Error("Group not found");
    
    const updatedMembers = groupSync.members.filter(member => member.userId !== user._id);
    
    if (updatedMembers.length === 0) {
      // Last member left, delete the group
      await ctx.db.delete(groupSync._id);
    } else {
      await ctx.db.patch(groupSync._id, {
        members: updatedMembers,
        updatedAt: Date.now(),
      });
    }
  },
});