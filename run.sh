#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [frontend|backend|both]"
    echo "  frontend - Build and run the frontend"
    echo "  backend  - Run the backend API"
    echo "  both     - Run both frontend and backend in parallel"
    exit 1
}

# Function to run frontend
run_frontend() {
    echo -e "${BLUE}Starting Frontend...${NC}"
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    # Start the development server
    echo -e "${GREEN}Starting frontend development server...${NC}"
    npm run dev
}

# Function to run backend
run_backend() {
    echo -e "${BLUE}Starting Backend...${NC}"
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${GREEN}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${GREEN}Installing backend dependencies...${NC}"
    pip install -r requirements.txt
    pip install "fastapi[standard]"
    
    # Run the FastAPI server
    echo -e "${GREEN}Starting FastAPI server...${NC}"
    fastapi dev src/api.py --port 8000
}

# Function to run both
run_both() {
    echo -e "${BLUE}Starting both Frontend and Backend...${NC}"
    
    # Run backend in background
    (run_backend) &
    BACKEND_PID=$!
    
    # Wait a bit for backend to start
    sleep 3
    
    # Run frontend
    (run_frontend) &
    FRONTEND_PID=$!
    
    echo -e "${GREEN}Both services are starting...${NC}"
    echo -e "${GREEN}Backend PID: $BACKEND_PID${NC}"
    echo -e "${GREEN}Frontend PID: $FRONTEND_PID${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop both services${NC}"
    
    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Main script
case "$1" in
    frontend)
        run_frontend
        ;;
    backend)
        run_backend
        ;;
    both)
        trap 'echo -e "${RED}Stopping services...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
        run_both
        ;;
    *)
        usage
        ;;
esac