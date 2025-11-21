#!/bin/bash

# Quick Start Script for New Features
# This script sets up and starts all necessary services

echo "🚀 Starting All-in-One Design Platform with New Features"
echo "========================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Redis is installed
echo -e "${YELLOW}Checking Redis...${NC}"
if ! command -v redis-server &> /dev/null; then
    echo -e "${RED}Redis is not installed. Please install Redis first.${NC}"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
    echo "  Windows: Download from https://github.com/microsoftarchive/redis/releases"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd backend
source venv/bin/activate
pip install -q pillow reportlab groq channels channels-redis

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOF
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
OPENAI_API_KEY=your-openai-key-here
GROQ_API_KEY=your-groq-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
    echo -e "${GREEN}.env file created. Please update with your API keys.${NC}"
fi

cd ..

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm install date-fns
cd ..

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Start Redis if not running
echo -e "${YELLOW}Starting Redis...${NC}"
if check_port 6379; then
    echo -e "${GREEN}Redis is already running${NC}"
else
    redis-server --daemonize yes
    sleep 2
    if check_port 6379; then
        echo -e "${GREEN}Redis started successfully${NC}"
    else
        echo -e "${RED}Failed to start Redis${NC}"
        exit 1
    fi
fi

# Create tmux session for running all services
if command -v tmux &> /dev/null; then
    echo -e "${YELLOW}Starting services in tmux session...${NC}"
    
    # Create new tmux session
    tmux new-session -d -s aidesign
    
    # Window 0: Django
    tmux rename-window -t aidesign:0 'Django'
    tmux send-keys -t aidesign:0 'cd backend && source venv/bin/activate && python manage.py runserver' C-m
    
    # Window 1: Celery
    tmux new-window -t aidesign:1 -n 'Celery'
    tmux send-keys -t aidesign:1 'cd backend && source venv/bin/activate && celery -A backend worker -B -l info' C-m
    
    # Window 2: Frontend
    tmux new-window -t aidesign:2 -n 'Frontend'
    tmux send-keys -t aidesign:2 'cd frontend && npm run dev' C-m
    
    # Window 3: Logs
    tmux new-window -t aidesign:3 -n 'Logs'
    tmux send-keys -t aidesign:3 'cd backend && tail -f logs/*.log' C-m
    
    echo ""
    echo -e "${GREEN}✅ All services started successfully!${NC}"
    echo ""
    echo "Services running:"
    echo "  - Redis:    localhost:6379"
    echo "  - Django:   http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Celery:   Running in background"
    echo ""
    echo "To view services: tmux attach -t aidesign"
    echo "To stop services: tmux kill-session -t aidesign"
    echo ""
    echo "Tmux controls:"
    echo "  - Switch windows: Ctrl+b then window number (0-3)"
    echo "  - Detach: Ctrl+b then d"
    echo "  - Kill session: tmux kill-session -t aidesign"
    echo ""
    
    # Attach to tmux session
    tmux attach -t aidesign
    
else
    echo -e "${YELLOW}tmux not found. Starting services manually...${NC}"
    echo -e "${YELLOW}Please open separate terminals for:${NC}"
    echo ""
    echo "Terminal 1 (Django):"
    echo "  cd backend && source venv/bin/activate && python manage.py runserver"
    echo ""
    echo "Terminal 2 (Celery):"
    echo "  cd backend && source venv/bin/activate && celery -A backend worker -B -l info"
    echo ""
    echo "Terminal 3 (Frontend):"
    echo "  cd frontend && npm run dev"
    echo ""
    echo "Then access:"
    echo "  - Django:   http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
fi
