#!/bin/bash
# Deployment script for CROPS Price Tracker
# Path: scripts/deploy.sh

set -e

echo "🚀 Deploying CROPS Price Tracker..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check environment
if [ "$1" = "production" ]; then
    ENV="production"
    echo -e "${BLUE}Deploying to PRODUCTION environment${NC}"
else
    ENV="staging"
    echo -e "${BLUE}Deploying to STAGING environment${NC}"
fi

# Build Frontend
echo -e "${BLUE}Building frontend...${NC}"
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}Frontend build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend built successfully${NC}"

# Deploy Frontend to Vercel
echo -e "${BLUE}Deploying frontend to Vercel...${NC}"
if [ "$ENV" = "production" ]; then
    vercel --prod
else
    vercel
fi
echo -e "${GREEN}✅ Frontend deployed${NC}"

cd ..

# Build Backend Docker Image
echo -e "${BLUE}Building backend Docker image...${NC}"
docker build -f infrastructure/docker/Dockerfile.backend -t crops-backend:latest ./backend
if [ $? -ne 0 ]; then
    echo -e "${RED}Backend Docker build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend Docker image built${NC}"

# Build Scraper Docker Image
echo -e "${BLUE}Building scraper Docker image...${NC}"
docker build -f infrastructure/docker/Dockerfile.scraper -t crops-scraper:latest ./backend
echo -e "${GREEN}✅ Scraper Docker image built${NC}"

# Deploy to Cloud (Railway/Render)
if [ "$ENV" = "production" ]; then
    echo -e "${BLUE}Deploying to production cloud...${NC}"
    
    # Tag images for registry
    docker tag crops-backend:latest registry.railway.app/crops-backend:latest
    docker tag crops-scraper:latest registry.railway.app/crops-scraper:latest
    
    # Push to registry
    docker push registry.railway.app/crops-backend:latest
    docker push registry.railway.app/crops-scraper:latest
    
    echo -e "${GREEN}✅ Deployed to production${NC}"
else
    echo -e "${BLUE}Running staging deployment locally...${NC}"
    
    # Start services with docker-compose
    docker-compose up -d
    
    echo -e "${GREEN}✅ Staging services started${NC}"
fi

# Run database migrations
echo -e "${BLUE}Running database migrations...${NC}"
cd backend
alembic upgrade head
echo -e "${GREEN}✅ Database migrations complete${NC}"

# Health check
echo -e "${BLUE}Running health checks...${NC}"
sleep 5

# Check backend health
BACKEND_URL="http://localhost:8000/health"
if curl -f $BACKEND_URL > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "📝 Deployment Summary:"
echo "   Environment: $ENV"
echo "   Frontend: Deployed to Vercel"
echo "   Backend: Deployed to cloud/docker"
echo "   Database: Migrations applied"
echo ""
echo "🔗 URLs:"
if [ "$ENV" = "production" ]; then
    echo "   Frontend: https://crops-tracker.vercel.app"
    echo "   Backend: https://api.crops-tracker.com"
else
    echo "   Frontend: https://crops-tracker-staging.vercel.app"
    echo "   Backend: http://localhost:8000"
fi