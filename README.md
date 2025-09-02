# Terminal 1: Database & Cache
This terminal runs your PostgreSQL database and Redis cache in the background using Docker. These services are required for the backend to store data and manage tasks. 

## Navigate to the project root directory
cd /c/crops-price-tracker

## Start the services
docker compose up -d

<br>
<br>


# Terminal 2: Backend API Server
This terminal runs the FastAPI application using the Uvicorn server. It handles all the API requests from the frontend, interacts with the database, and creates tasks for Celery.

## Navigate to the backend directory
cd /c/crops-price-tracker/backend

## Activate the Python virtual environment
source venv/Scripts/activate

## Start the Uvicorn server
uvicorn app.main:app --reload --port 8000


<br>
<br>

# Terminal 3: Task Execution (Celery Worker)
This terminal runs the Celery worker, which listens for and executes background tasks, such as web scraping. It's the "doer" of the backend.

## Navigate to the backend directory
cd /c/crops-price-tracker/backend

## Activate the Python virtual environment
source venv/Scripts/activate

## Start the Celery worker
celery -A app.tasks.celery_app worker --loglevel=info


<br>
<br>

# Terminal 4: Task Scheduling (Celery Beat)
This terminal runs the Celery beat scheduler. Its only job is to tell the Celery worker when to run scheduled tasks (e.g., "scrape prices every 5 minutes").

## Navigate to the backend directory
cd /c/crops-price-tracker/backend

## Activate the Python virtual environment
source venv/Scripts/activate

## Start the Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info


<br>
<br>


# Terminal 5: Frontend Application
This terminal runs the Next.js development server. This is the user-facing part of your application that people will see and interact with in their web browser.

## Navigate to the frontend directory
cd /c/crops-price-tracker/frontend

## Start the Next.js server
npm run dev














# CROPS Price Tracker 🌱

Real-time grocery price tracking system for Egyptian markets. Monitor prices across 10+ stores, track trends, and get instant alerts for price changes.

## 🚀 Features

- **Real-time Price Tracking**: Automated web scraping from Egyptian grocery stores
- **Live Updates**: WebSocket connections for instant price updates
- **Price Trends**: Historical data visualization with interactive charts
- **Stock Monitoring**: Track product availability across stores
- **Smart Categorization**: Automatic organic vs regular classification
- **Price Normalization**: Compare prices per kilogram across different pack sizes
- **Multi-store Support**: Gourmet Egypt, Metro, Spinneys, RDNA, and more
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Docker and Docker Compose
- PostgreSQL (via Docker)
- Redis (via Docker)

## 🛠️ Quick Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/crops-price-tracker.git
cd crops-price-tracker
```

### 2. Run the setup script
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Start PostgreSQL and Redis via Docker
- Install all dependencies
- Set up the database
- Create admin and demo users
- Start all services

### 3. Access the application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/docs
- **Admin Login**: admin@cropsegypt.com / admin123456
- **Demo Login**: demo@cropsegypt.com / demo123456

## 🔧 Manual Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Start services
docker-compose up -d
uvicorn app.main:app --reload --port 8000
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
cd backend
python -m app.utils.seeder
```

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Python, SQLAlchemy, Celery
- **Database**: PostgreSQL, Redis
- **Scraping**: Playwright, BeautifulSoup4
- **Deployment**: Vercel (Frontend), Railway/Render (Backend)

### Project Structure
```
crops-price-tracker/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── database/          # Seeds and migrations
├── scripts/           # Setup and deployment scripts
└── docs/             # Documentation
```

## 📊 API Documentation

Once the backend is running, visit http://localhost:8000/api/docs for interactive API documentation.

### Key Endpoints
- `POST /api/auth/login` - User authentication
- `GET /api/prices` - Get current prices
- `POST /api/prices/refresh` - Trigger price refresh
- `GET /api/products` - List all products
- `GET /api/stores` - List all stores
- `WS /ws` - WebSocket for real-time updates

## 🧪 Testing

### Run all tests
```bash
./scripts/test.sh
```

### Backend tests
```bash
cd backend
pytest
```

### Frontend tests
```bash
cd frontend
npm run test
npm run test:e2e
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Railway/Render)
1. Push to GitHub
2. Connect repository to Railway/Render
3. Set environment variables
4. Deploy

## 🔑 Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-jwt-secret
CELERY_BROKER_URL=redis://localhost:6379/0
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

CROPS Egypt - support@cropsegypt.com

Project Link: [https://github.com/yourusername/crops-price-tracker](https://github.com/yourusername/crops-price-tracker)

## 🙏 Acknowledgments

- SPC for Advanced Agriculture
- All Egyptian grocery stores for their data
- Open source community for amazing tools