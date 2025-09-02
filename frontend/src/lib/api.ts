// API client for backend communication
// Path: frontend/src/lib/api.ts

import axios, { AxiosInstance, AxiosError } from 'axios';
import { toast } from 'react-hot-toast';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          localStorage.removeItem('token');
          window.location.href = '/auth/login';
        } else if (error.response?.status === 500) {
          toast.error('Server error. Please try again later.');
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/api/auth/login', {
      username: email, // OAuth2 expects username field
      password,
    });
    return response.data;
  }

  async register(data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) {
    const response = await this.client.post('/api/auth/register', data);
    return response.data;
  }

  async getSession() {
    const response = await this.client.get('/api/auth/session');
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/auth/me');
    return response.data;
  }

  // Price endpoints
  async getPrices(params?: {
    skip?: number;
    limit?: number;
    product_id?: number;
    store_id?: number;
    category?: string;
    is_available?: boolean;
  }) {
    const response = await this.client.get('/api/prices', { params });
    return response.data;
  }

  async refreshPrices() {
    const response = await this.client.post('/api/prices/refresh');
    return response.data;
  }

  async getPriceTrends(productId: number, days: number = 7, storeId?: number) {
    const params = { product_id: productId, days, store_id: storeId };
    const response = await this.client.get('/api/prices/trends', { params });
    return response.data;
  }

  // Product endpoints
  async getProducts(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    is_organic?: boolean;
    search?: string;
  }) {
    const response = await this.client.get('/api/products', { params });
    return response.data;
  }

  async getProduct(id: number) {
    const response = await this.client.get(`/api/products/${id}`);
    return response.data;
  }

  async createProduct(data: {
    name: string;
    category: string;
    keywords?: string[];
    description?: string;
    is_organic?: boolean;
  }) {
    const response = await this.client.post('/api/products', data);
    return response.data;
  }

  async updateProduct(id: number, data: any) {
    const response = await this.client.put(`/api/products/${id}`, data);
    return response.data;
  }

  async deleteProduct(id: number) {
    const response = await this.client.delete(`/api/products/${id}`);
    return response.data;
  }

  // Store endpoints
  async getStores(params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }) {
    const response = await this.client.get('/api/stores', { params });
    return response.data;
  }

  async getStore(id: number) {
    const response = await this.client.get(`/api/stores/${id}`);
    return response.data;
  }

  async createStore(data: {
    name: string;
    url: string;
    type?: string;
    scraper_class: string;
    is_active?: boolean;
  }) {
    const response = await this.client.post('/api/stores', data);
    return response.data;
  }

  async updateStore(id: number, data: any) {
    const response = await this.client.put(`/api/stores/${id}`, data);
    return response.data;
  }

  async deleteStore(id: number) {
    const response = await this.client.delete(`/api/stores/${id}`);
    return response.data;
  }

  // Scraper endpoints
  async triggerScraping(storeId?: number) {
    const params = storeId ? { store_id: storeId } : {};
    const response = await this.client.post('/api/scraper/trigger', {}, { params });
    return response.data;
  }

  async getScrapingStatus() {
    const response = await this.client.get('/api/scraper/status');
    return response.data;
  }

  async stopScraping() {
    const response = await this.client.post('/api/scraper/stop');
    return response.data;
  }
}

export const api = new ApiClient();