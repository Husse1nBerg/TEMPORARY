// Authentication utilities
// Path: frontend/src/lib/auth.ts

import { api } from './api';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

class AuthManager {
  private user: User | null = null;

  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await api.login(email, password);
      
      if (response.access_token) {
        localStorage.setItem('token', response.access_token);
        
        // Get user info
        this.user = await this.getCurrentUser();
      }
      
      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async register(data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }): Promise<User> {
    try {
      const user = await api.register(data);
      return user;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token');
    this.user = null;
    window.location.href = '/auth/login';
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      if (!this.isAuthenticated()) {
        return null;
      }
      
      if (this.user) {
        return this.user;
      }
      
      const user = await api.getCurrentUser();
      this.user = user;
      return user;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  async checkSession(): Promise<boolean> {
    try {
      const response = await api.getSession();
      return response.valid === true;
    } catch (error) {
      return false;
    }
  }
}

export const auth = new AuthManager();