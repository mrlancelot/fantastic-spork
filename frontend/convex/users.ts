import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const store = mutation({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Called storeUser without authentication present");
    }

    // Check if we've already stored this identity before
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    if (user !== null) {
      // If the user is already stored, update their information
      const updateData: any = {
        email: identity.email || identity.user_id,
        emailVerified: identity.email_verified,
        name: identity.name,
        firstName: identity.given_name,
        lastName: identity.family_name,
        username: identity.username,
        imageUrl: identity.picture,
        hasImage: identity.has_image,
        phoneNumber: identity.phone,
        phoneVerified: identity.phone_verified,
        twoFactorEnabled: identity.two_factor_enabled,
        externalId: identity.external_id,
        lastSignInAt: identity.last_sign_in_at,
        updatedAt: Date.now(),
      };

      // Remove undefined values
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === undefined) {
          delete updateData[key];
        }
      });

      await ctx.db.patch(user._id, updateData);
      return user._id;
    }

    // If it's a new user, create a new document
    const newUser: any = {
      clerkId: identity.subject,
      email: identity.email || identity.user_id,
      emailVerified: identity.email_verified,
      name: identity.name,
      firstName: identity.given_name,
      lastName: identity.family_name,
      username: identity.username,
      imageUrl: identity.picture,
      hasImage: identity.has_image,
      phoneNumber: identity.phone,
      phoneVerified: identity.phone_verified,
      twoFactorEnabled: identity.two_factor_enabled,
      externalId: identity.external_id,
      lastSignInAt: identity.last_sign_in_at,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    // Remove undefined values
    Object.keys(newUser).forEach(key => {
      if (newUser[key] === undefined) {
        delete newUser[key];
      }
    });

    return await ctx.db.insert("users", newUser);
  },
});

export const getMyUser = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null;
    }
    
    const user = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
      .unique();
    
    return user;
  },
});

export const getAllUsers = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return [];
    }
    
    return await ctx.db.query("users").collect();
  },
});

export const storeFromBackend = mutation({
  args: {
    clerkUserId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Check if user already exists
    const existingUser = await ctx.db
      .query("users")
      .withIndex("by_clerk_id", (q) => q.eq("clerkId", args.clerkUserId))
      .unique();
    
    if (existingUser !== null) {
      // Update existing user
      const updateData: any = {
        email: args.email,
        name: args.name,
        imageUrl: args.imageUrl,
        updatedAt: Date.now(),
      };

      // Remove undefined values
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === undefined) {
          delete updateData[key];
        }
      });

      await ctx.db.patch(existingUser._id, updateData);
      return existingUser._id;
    }

    // Create new user
    const newUser: any = {
      clerkId: args.clerkUserId,
      email: args.email,
      name: args.name,
      imageUrl: args.imageUrl,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    // Remove undefined values
    Object.keys(newUser).forEach(key => {
      if (newUser[key] === undefined) {
        delete newUser[key];
      }
    });

    return await ctx.db.insert("users", newUser);
  },
});

