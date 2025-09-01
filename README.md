## Terminal 1: Database & Cache
This terminal runs your PostgreSQL database and Redis cache in the background using Docker. These services are required for the backend to store data and manage tasks. 

# Navigate to the project root directory
cd /c/crops-price-tracker

## Start the services
docker compose up -d




## Terminal 2: Backend API Server
This terminal runs the FastAPI application using the Uvicorn server. It handles all the API requests from the frontend, interacts with the database, and creates tasks for Celery.

## Navigate to the backend directory
cd /c/crops-price-tracker/backend

## Activate the Python virtual environment
source venv/Scripts/activate

## Start the Uvicorn server
uvicorn app.main:app --reload --port 8000




## Terminal 3: Task Execution (Celery Worker)
This terminal runs the Celery worker, which listens for and executes background tasks, such as web scraping. It's the "doer" of the backend.

## Navigate to the backend directory
cd /c/crops-price-tracker/backend

## Activate the Python virtual environment
source venv/Scripts/activate

## Start the Celery worker
celery -A app.tasks.celery_app worker --loglevel=info





## Terminal 4: Task Scheduling (Celery Beat)
This terminal runs the Celery beat scheduler. Its only job is to tell the Celery worker when to run scheduled tasks (e.g., "scrape prices every 5 minutes").

## Navigate to the backend directory
cd /c/crops-price-tracker/backend

## Activate the Python virtual environment
source venv/Scripts/activate

## Start the Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info





## Terminal 5: Frontend Application
This terminal runs the Next.js development server. This is the user-facing part of your application that people will see and interact with in their web browser.

## Navigate to the frontend directory
cd /c/crops-price-tracker/frontend

## Start the Next.js server
npm run dev