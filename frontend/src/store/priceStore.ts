import { create } from 'zustand';
import { api } from '@/lib/api';
import type { Price } from '@/hooks/usePrices'; // Reusing the Price type

interface PriceState {
  prices: Price[];
  loading: boolean;
  filters: { category?: string; store_id?: number; limit?: number };
  setFilters: (newFilters: PriceState['filters']) => void;
  fetchPrices: () => Promise<void>;
}

export const usePriceStore = create<PriceState>((set, get) => ({
  prices: [],
  loading: true,
  filters: { limit: 50 },

  setFilters: (newFilters) => {
    set({ filters: { ...get().filters, ...newFilters } });
    get().fetchPrices();
  },

  fetchPrices: async () => {
    set({ loading: true });
    try {
      const data = await api.getPrices(get().filters);
      set({ prices: data });
    } catch (error) {
      console.error("Failed to fetch prices from store", error);
    } finally {
      set({ loading: false });
    }
  },
}));