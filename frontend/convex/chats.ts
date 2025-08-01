import { v } from "convex/values";
import { action, mutation, query } from "./_generated/server";

export const sendMessage = action({
  args: {
    message: v.string(),
    tripId: v.optional(v.id("trips")),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.runQuery(api.users.getMyUser);
    if (!user) {
      throw new Error("User not found");
    }

    // Get or create chat session
    let chat = await ctx.runQuery(api.chats.getOrCreateChat, {
      tripId: args.tripId,
    });

    // Add user message
    await ctx.runMutation(api.chats.addMessage, {
      chatId: chat._id,
      role: "user",
      content: args.message,
    });

    // Call the backend API to get AI response
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: args.message,
        context: args.tripId ? await ctx.runQuery(api.trips.getTrip, { id: args.tripId }) : null,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to get AI response");
    }

    const data = await response.json();

    // Add AI response
    await ctx.runMutation(api.chats.addMessage, {
      chatId: chat._id,
      role: "assistant",
      content: data.response,
    });

    return data.response;
  },
});

export const getOrCreateChat = query({
  args: {
    tripId: v.optional(v.id("trips")),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user) {
      throw new Error("User not found");
    }

    // Look for existing chat
    let chatQuery = ctx.db
      .query("chats")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.tripId) {
      chatQuery = ctx.db
        .query("chats")
        .withIndex("by_trip", (q) => q.eq("tripId", args.tripId));
    }

    const existingChat = await chatQuery.first();
    
    if (existingChat) {
      return existingChat;
    }

    // Create new chat
    const chatId = await ctx.db.insert("chats", {
      userId: user._id,
      tripId: args.tripId,
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });

    const newChat = await ctx.db.get(chatId);
    return newChat!;
  },
});

export const addMessage = mutation({
  args: {
    chatId: v.id("chats"),
    role: v.union(v.literal("user"), v.literal("assistant")),
    content: v.string(),
  },
  handler: async (ctx, args) => {
    const chat = await ctx.db.get(args.chatId);
    if (!chat) {
      throw new Error("Chat not found");
    }

    const newMessages = [
      ...chat.messages,
      {
        role: args.role,
        content: args.content,
        timestamp: Date.now(),
      },
    ];

    await ctx.db.patch(args.chatId, {
      messages: newMessages,
      updatedAt: Date.now(),
    });
  },
});

export const getChatMessages = query({
  args: {
    tripId: v.optional(v.id("trips")),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return [];
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (!user) {
      return [];
    }

    let chatQuery = ctx.db
      .query("chats")
      .withIndex("by_user", (q) => q.eq("userId", user._id));
    
    if (args.tripId) {
      chatQuery = ctx.db
        .query("chats")
        .withIndex("by_trip", (q) => q.eq("tripId", args.tripId));
    }

    const chat = await chatQuery.first();
    
    if (!chat) {
      return [];
    }

    return chat.messages;
  },
});

import { api } from "./_generated/api";