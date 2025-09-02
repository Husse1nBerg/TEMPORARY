#!/bin/bash
# Setup script for CROPS Price Tracker
# Path: scripts/setup.sh

echo "🚀 Setting up CROPS Price Tracker..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js (v18+) first.${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

echo -e "${BLUE}Starting database services...${NC}"
docker-compose up -d
sleep 5

echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Backend .env file created${NC}"
fi

# Run database migrations
echo -e "${BLUE}Setting up database...${NC}"
python -m app.utils.seeder

# Start backend in background
echo -e "${BLUE}Starting backend server...${NC}"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Celery worker
echo -e "${BLUE}Starting Celery worker...${NC}"
celery -A app.tasks.celery_app worker --loglevel=info &
CELERY_PID=$!

cd ..

echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend

# Install dependencies
npm install

# Copy environment file
if [ ! -f .env.local ]; then
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://localhost:3000
EOF
    echo -e "${GREEN}✅ Frontend .env.local file created${NC}"
fi

# Build frontend
echo -e "${BLUE}Building frontend...${NC}"
npm run build

# Start frontend
echo -e "${BLUE}Starting frontend server...${NC}"
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✨ Setup complete!${NC}"
echo ""
echo "📝 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api/docs"
echo ""
echo "🔑 Login credentials:"
echo "   Admin: admin@cropsegypt.com / admin123456"
echo "   Demo: demo@cropsegypt.com / demo123456"
echo ""
echo "📊 Services running:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - Backend: localhost:8000 (PID: $BACKEND_PID)"
echo "   - Frontend: localhost:3000 (PID: $FRONTEND_PID)"
echo "   - Celery: (PID: $CELERY_PID)"
echo ""
echo "To stop all services, run: ./scripts/stop.sh"