"""
Convex Mutation Definitions
These need to be deployed to Convex as serverless functions
"""

# Note: These are the mutation definitions that should be created in your Convex deployment
# You'll need to create these mutations in your Convex dashboard or via Convex CLI

MUTATIONS = {
    "create_itinerary": """
        export default mutation({
            args: {
                id: v.string(),
                user_id: v.optional(v.string()),
                destination: v.string(),
                start_date: v.string(),
                end_date: v.string(),
                status: v.string(),
                created_at: v.string(),
                updated_at: v.string()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("itineraries", args);
            }
        });
    """,
    
    "create_itinerary_day": """
        export default mutation({
            args: {
                id: v.string(),
                itinerary_id: v.string(),
                day_number: v.number(),
                date: v.string()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("itinerary_days", args);
            }
        });
    """,
    
    "create_activity": """
        export default mutation({
            args: {
                id: v.string(),
                itinerary_day_id: v.string(),
                title: v.string(),
                time: v.string(),
                duration: v.string(),
                location: v.string(),
                activity_type: v.string(),
                additional_info: v.optional(v.string()),
                order: v.number()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("activities", args);
            }
        });
    """,
    
    "create_flight": """
        export default mutation({
            args: {
                id: v.string(),
                itinerary_id: v.optional(v.string()),
                origin: v.string(),
                destination: v.string(),
                airline: v.string(),
                flight_number: v.optional(v.string()),
                departure_date: v.string(),
                arrival_date: v.optional(v.string()),
                price: v.number(),
                stops: v.number(),
                duration: v.optional(v.string()),
                booking_url: v.optional(v.string()),
                created_at: v.string()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("flights", args);
            }
        });
    """,
    
    "create_hotel": """
        export default mutation({
            args: {
                id: v.string(),
                itinerary_id: v.optional(v.string()),
                name: v.string(),
                address: v.string(),
                check_in_date: v.string(),
                check_out_date: v.string(),
                price: v.number(),
                rating: v.optional(v.number()),
                amenities: v.array(v.string()),
                source: v.string(),
                property_type: v.optional(v.string()),
                booking_url: v.optional(v.string()),
                image_url: v.optional(v.string()),
                reviews_count: v.optional(v.number()),
                created_at: v.string()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("hotels", args);
            }
        });
    """,
    
    "create_restaurant": """
        export default mutation({
            args: {
                id: v.string(),
                itinerary_id: v.optional(v.string()),
                name: v.string(),
                address: v.string(),
                cuisine: v.array(v.string()),
                price_range: v.string(),
                rating: v.optional(v.number()),
                phone: v.optional(v.string()),
                website: v.optional(v.string()),
                hours: v.optional(v.string()),
                status: v.string(),
                source_url: v.optional(v.string()),
                description: v.optional(v.string()),
                created_at: v.string()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("restaurants", args);
            }
        });
    """,
    
    "create_job": """
        export default mutation({
            args: {
                id: v.string(),
                type: v.string(),
                status: v.string(),
                progress: v.number(),
                input: v.optional(v.string()),
                result: v.optional(v.string()),
                error: v.optional(v.string()),
                created_at: v.string(),
                updated_at: v.string()
            },
            handler: async (ctx, args) => {
                return await ctx.db.insert("jobs", args);
            }
        });
    """,
    
    "update_job": """
        export default mutation({
            args: {
                job_id: v.string(),
                status: v.string(),
                progress: v.optional(v.number()),
                result: v.optional(v.string()),
                error: v.optional(v.string())
            },
            handler: async (ctx, args) => {
                const job = await ctx.db
                    .query("jobs")
                    .filter((q) => q.eq(q.field("id"), args.job_id))
                    .first();
                
                if (!job) {
                    throw new Error("Job not found");
                }
                
                const updateData = {
                    status: args.status,
                    updated_at: new Date().toISOString()
                };
                
                if (args.progress !== undefined) {
                    updateData.progress = args.progress;
                }
                if (args.result !== undefined) {
                    updateData.result = args.result;
                }
                if (args.error !== undefined) {
                    updateData.error = args.error;
                }
                
                return await ctx.db.patch(job._id, updateData);
            }
        });
    """
}

# Schema definitions for Convex tables
SCHEMA = {
    "itineraries": {
        "id": "string",
        "user_id": "string?",
        "destination": "string",
        "start_date": "string",
        "end_date": "string",
        "status": "string",
        "created_at": "string",
        "updated_at": "string"
    },
    
    "itinerary_days": {
        "id": "string",
        "itinerary_id": "string",
        "day_number": "number",
        "date": "string"
    },
    
    "activities": {
        "id": "string",
        "itinerary_day_id": "string",
        "title": "string",
        "time": "string",
        "duration": "string",
        "location": "string",
        "activity_type": "string",
        "additional_info": "string?",
        "order": "number"
    },
    
    "flights": {
        "id": "string",
        "itinerary_id": "string?",
        "origin": "string",
        "destination": "string",
        "airline": "string",
        "flight_number": "string?",
        "departure_date": "string",
        "arrival_date": "string?",
        "price": "number",
        "stops": "number",
        "duration": "string?",
        "booking_url": "string?",
        "created_at": "string"
    },
    
    "hotels": {
        "id": "string",
        "itinerary_id": "string?",
        "name": "string",
        "address": "string",
        "check_in_date": "string",
        "check_out_date": "string",
        "price": "number",
        "rating": "number?",
        "amenities": "array<string>",
        "source": "string",
        "property_type": "string?",
        "booking_url": "string?",
        "image_url": "string?",
        "reviews_count": "number?",
        "created_at": "string"
    },
    
    "restaurants": {
        "id": "string",
        "itinerary_id": "string?",
        "name": "string",
        "address": "string",
        "cuisine": "array<string>",
        "price_range": "string",
        "rating": "number?",
        "phone": "string?",
        "website": "string?",
        "hours": "string?",
        "status": "string",
        "source_url": "string?",
        "description": "string?",
        "created_at": "string"
    },
    
    "jobs": {
        "id": "string",
        "type": "string",
        "status": "string",
        "progress": "number",
        "input": "string?",
        "result": "string?",
        "error": "string?",
        "created_at": "string",
        "updated_at": "string"
    }
}