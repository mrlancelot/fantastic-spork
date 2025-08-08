#!/bin/bash

# Start backend with enhanced logging
echo "Starting TravelAI Backend with enhanced logging..."
echo "================================"

# Set environment variable for better debugging
export PYTHONUNBUFFERED=1
export LOG_LEVEL=DEBUG

# Start the backend
cd /Users/pridhvi/Documents/Github/fantastic-spork/backend
python src/api.py 2>&1 | tee backend.log