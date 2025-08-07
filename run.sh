#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [frontend|backend|convex|all]"
    echo "  frontend - Run the frontend development server"
    echo "  backend  - Run the backend API server"
    echo "  convex   - Run Convex development server"
    echo "  all      - Run all three services (frontend, backend, convex)"
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
    
    # Install dependencies if requirements.txt is newer than venv
    if [ "requirements.txt" -nt "venv" ] || [ ! -f "venv/.deps_installed" ]; then
        echo -e "${GREEN}Installing backend dependencies...${NC}"
        pip install -r requirements.txt
        pip install "fastapi[standard]"
        touch venv/.deps_installed
    fi
    
    # Run the FastAPI server using the new main.py
    echo -e "${GREEN}Starting FastAPI server on port 8000...${NC}"
    python -m src.main
}

# Function to run Convex
run_convex() {
    echo -e "${BLUE}Starting Convex...${NC}"
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}Installing frontend dependencies for Convex...${NC}"
        npm install
    fi
    
    echo -e "${GREEN}Starting Convex development server...${NC}"
    npx convex dev
}

# Function to run all services
run_all() {
    echo -e "${BLUE}Starting all services (Frontend, Backend, Convex)...${NC}"
    
    # Run backend in background
    (run_backend) &
    BACKEND_PID=$!
    
    # Run convex in background
    (run_convex) &
    CONVEX_PID=$!
    
    # Wait a bit for backend and convex to start
    sleep 5
    
    # Run frontend in background
    (run_frontend) &
    FRONTEND_PID=$!
    
    echo -e "${GREEN}All services are running:${NC}"
    echo -e "${GREEN}  Backend PID:  $BACKEND_PID  (http://localhost:8000)${NC}"
    echo -e "${GREEN}  Convex PID:   $CONVEX_PID   (Convex Dashboard)${NC}"
    echo -e "${GREEN}  Frontend PID: $FRONTEND_PID (http://localhost:5173)${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
    
    # Wait for all processes
    wait $BACKEND_PID $CONVEX_PID $FRONTEND_PID
}

# Main script
case "$1" in
    frontend)
        run_frontend
        ;;
    backend)
        run_backend
        ;;
    convex)
        run_convex
        ;;
    all)
        trap 'echo -e "${RED}Stopping all services...${NC}"; kill $BACKEND_PID $CONVEX_PID $FRONTEND_PID 2>/dev/null; exit' INT
        run_all
        ;;
    *)
        usage
        ;;
esac