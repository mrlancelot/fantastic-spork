#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ASCII Art Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║        TravelAI Development Server      ║"
    echo "║         🚀 Web Scraper Edition 🚀       ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to display usage
usage() {
    print_banner
    echo "Usage: $0 [frontend|backend|convex|both|all|status|stop]"
    echo ""
    echo "Commands:"
    echo "  frontend - Run the frontend development server"
    echo "  backend  - Run the backend API server with scrapers"
    echo "  convex   - Run Convex development server (requires configuration)"
    echo "  both     - Run frontend and backend (recommended)"
    echo "  all      - Run all three services (frontend, backend, convex)"
    echo "  status   - Check status of all services"
    echo "  stop     - Stop all running services"
    echo ""
    echo "Examples:"
    echo "  $0 both     # Start frontend and backend"
    echo "  $0 backend  # Start only backend API"
    exit 1
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for $service to start...${NC}"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null; then
            echo -e "${GREEN}✓ $service is ready!${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e "${RED}✗ $service failed to start${NC}"
    return 1
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
    
    # Check for .env file
    if [ ! -f "../.env" ] && [ ! -f ".env" ]; then
        echo -e "${RED}Warning: .env file not found!${NC}"
        echo -e "${BLUE}Creating .env.example for reference...${NC}"
        cat > .env.example << EOF
# AI Services (Required)
GEMINI_API_KEY=your_gemini_api_key

# Restaurant Service (Required)
TAVILY_API_KEY=your_tavily_api_key

# Optional Services
OPENROUTER_API_KEY=your_openrouter_key
CLERK_SECRET_KEY=sk_test_...
CONVEX_URL=https://your-deployment.convex.cloud
CONVEX_DEPLOYMENT=production

# Scraper Settings
SCRAPER_HEADLESS=true
EOF
        echo -e "${BLUE}Please create a .env file with your API keys.${NC}"
        echo -e "${BLUE}You can copy .env.example to .env and fill in your keys.${NC}"
    fi
    
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
    
    # Install Playwright browsers if not installed
    if ! playwright show chromium &>/dev/null; then
        echo -e "${GREEN}Installing Playwright browsers...${NC}"
        playwright install chromium
    fi
    
    # Run the backend server using main.py
    echo -e "${GREEN}Starting FastAPI server on port 8000...${NC}"
    python main.py
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
    
    # Check if Convex is configured
    if [ ! -f ".env.local" ] || ! grep -q "VITE_CONVEX_URL" .env.local 2>/dev/null; then
        echo -e "${RED}Convex is not configured yet!${NC}"
        echo -e "${BLUE}Please configure Convex first by running:${NC}"
        echo -e "  cd frontend"
        echo -e "  npx convex dev"
        echo -e "${BLUE}Then follow the prompts to set up your Convex project.${NC}"
        echo -e "${BLUE}After configuration, run this script again.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Starting Convex development server...${NC}"
    npx convex dev --once
}

# Function to run all services
run_all() {
    echo -e "${BLUE}Starting all services (Frontend, Backend, Convex)...${NC}"
    
    # Check if Convex is configured before attempting to run all
    cd frontend
    if [ ! -f ".env.local" ] || ! grep -q "VITE_CONVEX_URL" .env.local 2>/dev/null; then
        echo -e "${RED}Warning: Convex is not configured.${NC}"
        echo -e "${BLUE}Running only Frontend and Backend. Configure Convex separately.${NC}"
        cd ..
        
        # Run backend in background
        (run_backend) &
        BACKEND_PID=$!
        
        # Wait a bit for backend to start
        sleep 3
        
        # Run frontend in background
        (run_frontend) &
        FRONTEND_PID=$!
        
        echo -e "${GREEN}Services are running:${NC}"
        echo -e "${GREEN}  Backend PID:  $BACKEND_PID  (http://localhost:8000)${NC}"
        echo -e "${GREEN}  Frontend PID: $FRONTEND_PID (http://localhost:5173)${NC}"
        echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
        
        # Wait for processes
        wait $BACKEND_PID $FRONTEND_PID
    else
        cd ..
        
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
    fi
}

# Function to run frontend and backend only
run_both() {
    echo -e "${BLUE}Starting Frontend and Backend...${NC}"
    echo ""
    
    # Check if ports are already in use
    if check_port 8000; then
        echo -e "${RED}Error: Port 8000 is already in use (Backend)${NC}"
        echo -e "${YELLOW}Run '$0 stop' to stop all services first${NC}"
        exit 1
    fi
    
    if check_port 5173; then
        echo -e "${RED}Error: Port 5173 is already in use (Frontend)${NC}"
        echo -e "${YELLOW}Run '$0 stop' to stop all services first${NC}"
        exit 1
    fi
    
    # Run backend in background
    (run_backend) &
    BACKEND_PID=$!
    
    # Wait for backend to be ready
    wait_for_service "http://localhost:8000/api/health" "Backend API"
    
    # Run frontend in background
    (run_frontend) &
    FRONTEND_PID=$!
    
    # Wait a moment for frontend to start
    sleep 3
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ All services are running successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "  📡 Backend API:  ${GREEN}http://localhost:8000${NC}"
    echo -e "  📚 API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  🎨 Frontend:     ${GREEN}http://localhost:5173${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""
    
    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Function to check status
check_status() {
    echo -e "${BLUE}Checking service status...${NC}"
    echo ""
    
    # Check Backend
    if check_port 8000; then
        echo -e "${GREEN}✓ Backend API is running on port 8000${NC}"
        # Try to get health status
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo -e "  ${GREEN}API Health: OK${NC}"
        fi
    else
        echo -e "${RED}✗ Backend API is not running${NC}"
    fi
    
    # Check Frontend
    if check_port 5173; then
        echo -e "${GREEN}✓ Frontend is running on port 5173${NC}"
    else
        echo -e "${RED}✗ Frontend is not running${NC}"
    fi
    
    # Check Convex (if configured)
    if check_port 3210; then
        echo -e "${GREEN}✓ Convex is running on port 3210${NC}"
    else
        echo -e "${YELLOW}⚠ Convex is not running (optional)${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "  Backend API:  http://localhost:8000"
    echo -e "  API Docs:     http://localhost:8000/docs"
    echo -e "  Frontend:     http://localhost:5173"
}

# Function to stop all services
stop_all() {
    echo -e "${RED}Stopping all services...${NC}"
    
    # Kill processes on specific ports
    for port in 8000 5173 3210; do
        if check_port $port; then
            echo -e "${YELLOW}Stopping service on port $port...${NC}"
            lsof -ti:$port | xargs kill -9 2>/dev/null
        fi
    done
    
    echo -e "${GREEN}All services stopped.${NC}"
}

# Main script
case "$1" in
    frontend)
        print_banner
        run_frontend
        ;;
    backend)
        print_banner
        run_backend
        ;;
    convex)
        print_banner
        run_convex
        ;;
    both)
        print_banner
        trap 'echo -e "${RED}Stopping services...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
        run_both
        ;;
    all)
        print_banner
        trap 'echo -e "${RED}Stopping all services...${NC}"; kill $BACKEND_PID $CONVEX_PID $FRONTEND_PID 2>/dev/null; exit' INT
        run_all
        ;;
    status)
        print_banner
        check_status
        ;;
    stop)
        print_banner
        stop_all
        ;;
    *)
        usage
        ;;
esac