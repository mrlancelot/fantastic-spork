#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}Waypoint - Travel Planning Application${NC}"
    echo ""
    echo "Usage: $0 [frontend|backend|all]"
    echo "  frontend - Run the frontend development server"
    echo "  backend  - Run the backend API server"
    echo "  all      - Run both frontend and backend services"
    echo ""
    echo "The application will be available at:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend:  http://localhost:8000"
    exit 1
}

# Function to check and install frontend dependencies
install_frontend_deps() {
    echo -e "${YELLOW}Checking frontend dependencies...${NC}"
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}Installing frontend dependencies...${NC}"
        npm install
    else
        echo -e "${GREEN}Frontend dependencies already installed${NC}"
    fi
    
    cd ..
}

# Function to check and install backend dependencies
install_backend_deps() {
    echo -e "${YELLOW}Checking backend dependencies...${NC}"
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${GREEN}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${GREEN}Installing/updating backend dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ..
}

# Function to run frontend
run_frontend() {
    echo -e "${BLUE}Starting Frontend...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    # Start the development server
    echo -e "${GREEN}Starting frontend development server on port 5173...${NC}"
    echo -e "${YELLOW}Frontend will be available at: http://localhost:5173${NC}"
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
        pip install --upgrade pip
        pip install -r requirements.txt
        touch venv/.deps_installed
    fi
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Warning: No .env file found in backend directory${NC}"
        echo -e "${YELLOW}Please create a .env file with your API keys:${NC}"
        echo "  OPENROUTER_API_KEY=your_key_here"
        echo "  AMADEUS_CLIENT_ID=your_id_here"
        echo "  AMADEUS_CLIENT_SECRET=your_secret_here"
        echo ""
    fi
    
    # Run the FastAPI server with the correct module path
    echo -e "${GREEN}Starting FastAPI server on port 8000...${NC}"
    echo -e "${YELLOW}Backend API will be available at: http://localhost:8000${NC}"
    echo -e "${YELLOW}API documentation: http://localhost:8000/docs${NC}"
    python main.py
}

# Function to run all services
run_all() {
    echo -e "${BLUE}Starting all services (Frontend & Backend)...${NC}"
    echo ""
    
    # Install all dependencies first
    install_backend_deps
    install_frontend_deps
    
    # Check for backend .env file
    if [ ! -f "backend/.env" ]; then
        echo -e "${RED}Error: No .env file found in backend directory${NC}"
        echo -e "${YELLOW}Please create backend/.env with your API keys:${NC}"
        echo "  OPENROUTER_API_KEY=your_key_here"
        echo "  AMADEUS_CLIENT_ID=your_id_here"
        echo "  AMADEUS_CLIENT_SECRET=your_secret_here"
        echo ""
        echo -e "${YELLOW}You can get these keys from:${NC}"
        echo "  OpenRouter: https://openrouter.ai/keys"
        echo "  Amadeus: https://developers.amadeus.com/"
        exit 1
    fi
    
    # Create a trap to handle Ctrl+C
    trap cleanup INT
    
    # Run backend in background
    echo -e "${GREEN}Starting Backend service...${NC}"
    (cd backend && source venv/bin/activate && python main.py) &
    BACKEND_PID=$!
    
    # Wait a bit for backend to start
    echo -e "${YELLOW}Waiting for backend to start...${NC}"
    sleep 3
    
    # Check if backend is running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}Backend failed to start. Check the logs above.${NC}"
        exit 1
    fi
    
    # Run frontend in background
    echo -e "${GREEN}Starting Frontend service...${NC}"
    (cd frontend && npm run dev) &
    FRONTEND_PID=$!
    
    # Wait a bit for frontend to start
    sleep 3
    
    # Check if frontend is running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}Frontend failed to start. Check the logs above.${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ All services are running successfully!${NC}"
    echo ""
    echo -e "${BLUE}Access the application:${NC}"
    echo -e "  🌐 Frontend:  ${GREEN}http://localhost:5173${NC}"
    echo -e "  🔧 Backend:   ${GREEN}http://localhost:8000${NC}"
    echo -e "  📚 API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""
    
    # Wait for all processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${RED}Stopping all services...${NC}"
    
    # Kill processes if they exist
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${YELLOW}Backend stopped${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${YELLOW}Frontend stopped${NC}"
    fi
    
    # Kill any remaining node or python processes related to our app
    pkill -f "npm run dev" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    pkill -f "python main.py" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null
    
    echo -e "${GREEN}All services stopped successfully${NC}"
    exit 0
}

# Main script
case "$1" in
    frontend)
        run_frontend
        ;;
    backend)
        run_backend
        ;;
    all)
        run_all
        ;;
    *)
        usage
        ;;
esac