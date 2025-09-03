'use client';

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

export interface Product {
    id: number;
    name: string;
    category: string;
    keywords: string[];
    description?: string;
    is_organic: boolean;
    is_active: boolean;
}

export function useProducts(initialFilters?: { category?: string; search?: string; }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState(initialFilters || {});

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getProducts(filters);
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const updateFilters = (newFilters: typeof filters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  return { products, loading, updateFilters, refetch: fetchProducts };
}