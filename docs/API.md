# In husse1nberg/temporary/TEMPORARY/docs/API.md
# CROPS Price Tracker API Documentation

This document provides a comprehensive overview of the CROPS Price Tracker API, including authentication, available endpoints, and real-time updates via WebSockets.

---

## **Authentication**

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, you must include an `Authorization` header with a Bearer token in your requests.

### **Register**

* **Endpoint**: `POST /api/auth/register`
* **Description**: Creates a new user account.
* **Request Body**:
    * `email` (string, required): The user's email address.
    * `username` (string, required): The user's username.
    * `password` (string, required): The user's password.
    * `full_name` (string, optional): The user's full name.
* **Response**: A user object with the new user's details.

### **Login**

* **Endpoint**: `POST /api/auth/login`
* **Description**: Authenticates a user and returns a JWT.
* **Request Body**:
    * `username` (string, required): The user's email or username.
    * `password` (string, required): The user's password.
* **Response**: An access token and token type.

---

## **API Endpoints**

### **Products**

* **`GET /api/products`**: Retrieves a list of all products with optional filters for `category`, `is_organic`, and `search`.
* **`POST /api/products`**: Creates a new product.
* **`GET /api/products/{product_id}`**: Retrieves a specific product by its ID.
* **`PUT /api/products/{product_id}`**: Updates a product's details.
* **`DELETE /api/products/{product_id}`**: Deletes a product.

### **Stores**

* **`GET /api/stores`**: Retrieves a list of all stores, with an optional filter for `is_active`.
* **`POST /api/stores`**: Creates a new store.
* **`GET /api/stores/{store_id}`**: Retrieves a specific store by its ID.
* **`PUT /api/stores/{store_id}`**: Updates a store's details.
* **`DELETE /api/stores/{store_id}`**: Deletes a store.

### **Prices**

* **`GET /api/prices`**: Retrieves a list of current prices with optional filters for `product_id`, `store_id`, `category`, and `is_available`.
* **`POST /api/prices/refresh`**: Triggers a price refresh for all stores.
* **`GET /api/prices/trends`**: Retrieves price trends for a specific product.
* **`GET /api/prices/{price_id}`**: Retrieves a specific price by its ID.

### **Scraper**

* **`POST /api/scraper/trigger`**: Triggers scraping for all stores or a specific store.
* **`GET /api/scraper/status`**: Retrieves the current scraping status for all stores.
* **`POST /api/scraper/stop`**: Stops all ongoing scraping tasks.

### **AI Analysis**

* **`POST /api/ai/analyze-trends`**: Provides AI-powered price trend analysis.
* **`POST /api/ai/predict-prices`**: Predicts future prices for a product.
* **`POST /api/ai/recommendations`**: Generates AI-powered buying recommendations.
* **`POST /api/ai/detect-anomaly`**: Detects if a price is an anomaly.

---

## **WebSockets**

The API provides a WebSocket endpoint for real-time price updates.

* **Endpoint**: `ws://localhost:8000/ws`
* **Description**: Establishes a WebSocket connection for receiving real-time price updates.