// Prices hook for React components
// Path: frontend/src/hooks/usePrices.ts

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { toast } from 'react-hot-toast';

export interface Price {
  id: number;
  product_id: number;
  product_name: string;
  product_category: string;
  store_id: number;
  store_name: string;
  price: number;
  original_price?: number;
  price_per_kg?: number;
  pack_size?: string;
  pack_unit?: string;
  is_available: boolean;
  is_discounted: boolean;
  is_organic: boolean;
  price_change: number;
  price_change_percent: number;
  product_url?: string;
  image_url?: string;
  scraped_at: string;
}

// UPDATE THIS TYPE DEFINITION
export function usePrices(initialFilters?: {
  category?: string;
  store_id?: number;
  is_available?: boolean;
  limit?: number; // Add limit
  skip?: number;  // Add skip
}) {
  const [prices, setPrices] = useState<Price[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filters, setFilters] = useState(initialFilters || {});

  const fetchPrices = useCallback(async () => {
    try {
      setLoading(true);
      // PASS THE FILTERS (INCLUDING LIMIT) TO THE API CALL
      const data = await api.getPrices({
        ...filters,
      });
      setPrices(data);
    } catch (error) {
      console.error('Error fetching prices:', error);
      toast.error('Failed to load prices');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const refreshPrices = async () => {
    try {
      setRefreshing(true);
      await api.refreshPrices();
      toast.success('Price refresh initiated! Updates will appear shortly.');
      
      // Wait a bit and then refresh the data
      setTimeout(() => {
        fetchPrices();
      }, 3000);
    } catch (error) {
      console.error('Error refreshing prices:', error);
      toast.error('Failed to refresh prices');
    } finally {
      setRefreshing(false);
    }
  };

  const updateFilters = (newFilters: typeof filters) => {
    setFilters(newFilters);
  };

  useEffect(() => {
    fetchPrices();
  }, [fetchPrices]);

  // Set up WebSocket for real-time updates
  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'price_update') {
        setPrices(prevPrices => {
          const index = prevPrices.findIndex(p => p.id === data.price.id);
          if (index >= 0) {
            const newPrices = [...prevPrices];
            newPrices[index] = data.price;
            return newPrices;
          }
          return [...prevPrices, data.price];
        });
        toast.success(`Price updated: ${data.price.product_name}`);
      }
    };

    return () => ws.close();
  }, []);

  return {
    prices,
    loading,
    refreshing,
    filters,
    updateFilters,
    refreshPrices,
    refetch: fetchPrices,
  };
}