/* eslint-disable */
/**
 * Generated `api` utility.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import type {
  ApiFromModules,
  FilterApi,
  FunctionReference,
} from "convex/server";
import type * as achievements from "../achievements.js";
import type * as chats from "../chats.js";
import type * as groupSync from "../groupSync.js";
import type * as journeys from "../journeys.js";
import type * as moodTracking from "../moodTracking.js";
import type * as richItineraries from "../richItineraries.js";
import type * as scrapbook from "../scrapbook.js";
import type * as searchCache from "../searchCache.js";
import type * as slots from "../slots.js";
import type * as travelDocs from "../travelDocs.js";
import type * as trips from "../trips.js";
import type * as users from "../users.js";

/**
 * A utility for referencing Convex functions in your app's API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = api.myModule.myFunction;
 * ```
 */
declare const fullApi: ApiFromModules<{
  achievements: typeof achievements;
  chats: typeof chats;
  groupSync: typeof groupSync;
  journeys: typeof journeys;
  moodTracking: typeof moodTracking;
  richItineraries: typeof richItineraries;
  scrapbook: typeof scrapbook;
  searchCache: typeof searchCache;
  slots: typeof slots;
  travelDocs: typeof travelDocs;
  trips: typeof trips;
  users: typeof users;
}>;
export declare const api: FilterApi<
  typeof fullApi,
  FunctionReference<any, "public">
>;
export declare const internal: FilterApi<
  typeof fullApi,
  FunctionReference<any, "internal">
>;
