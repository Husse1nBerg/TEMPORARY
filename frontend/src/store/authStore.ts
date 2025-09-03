import { create } from 'zustand';
import { api } from '@/lib/api';
import { TOKEN_KEY } from '@/lib/constants';

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const response = await api.login(email, password);
      localStorage.setItem(TOKEN_KEY, response.access_token);
      set({ token: response.access_token, isAuthenticated: true });
      await get().checkAuth();
    } catch (error) {
      set({ isAuthenticated: false, user: null, token: null });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    set({ user: null, token: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      set({ isAuthenticated: false, isLoading: false, user: null, token: null });
      return;
    }
    
    try {
      const user = await api.getCurrentUser();
      set({ user, token, isAuthenticated: true, isLoading: false });
    } catch (error) {
      get().logout();
      set({ isLoading: false });
    }
  },
}));