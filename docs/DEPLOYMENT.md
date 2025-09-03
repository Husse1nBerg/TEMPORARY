# In husse1nberg/temporary/TEMPORARY/docs/DEPLOYMENT.md
# Deployment Guide

This guide provides instructions for deploying the CROPS Price Tracker application, covering both the frontend and backend services.

---

## **Frontend Deployment (Vercel)**

The frontend is a Next.js application designed for easy deployment on Vercel.

1.  **Prerequisites**:
    * A Vercel account.
    * The project pushed to a Git repository (e.g., GitHub, GitLab).
2.  **Deployment Steps**:
    * Connect your Git repository to Vercel.
    * Configure the environment variables in the Vercel project settings.
    * Deploy the application. Vercel will automatically detect that it's a Next.js project and build it accordingly.

### **Environment Variables**

* `NEXT_PUBLIC_API_URL`: The URL of the backend API.
* `NEXT_PUBLIC_WEBSOCKET_URL`: The WebSocket URL for the backend.

---

## **Backend Deployment (Docker)**

The backend is a FastAPI application that can be deployed using Docker.

1.  **Build the Docker Image**:
    * Use the provided `Dockerfile.backend` to build the Docker image for the backend.
2.  **Run the Container**:
    * Run the Docker container, making sure to expose the correct port and provide the necessary environment variables.
3.  **Database and Redis**:
    * The backend requires a PostgreSQL database and a Redis instance, which can be set up using the `docker-compose.yml` file.

### **Environment Variables**

* `DATABASE_URL`: The connection string for the PostgreSQL database.
* `REDIS_URL`: The URL for the Redis instance.
* `SECRET_KEY`: A secret key for JWT authentication.
* `CORS_ORIGINS`: A comma-separated list of allowed origins for CORS.

---

## **Deployment Script**

The project includes a `deploy.sh` script in the `scripts` directory that automates the deployment process. You can customize this script to fit your specific deployment needs.