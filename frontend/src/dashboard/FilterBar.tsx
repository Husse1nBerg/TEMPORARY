'use client';

import { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api } from '@/lib/api';

interface Store {
  id: number;
  name: string;
}

interface FilterBarProps {
  onFilterChange: (filters: { storeId?: number; category?: string }) => void;
}

export default function FilterBar({ onFilterChange }: FilterBarProps) {
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStore, setSelectedStore] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  useEffect(() => {
    // Fetch stores for the dropdown
    const fetchStores = async () => {
      try {
        const storeData = await api.getStores();
        setStores(storeData);
      } catch (error) {
        console.error("Failed to fetch stores for filter", error);
      }
    };
    fetchStores();
  }, []);

  useEffect(() => {
    // Notify parent component of filter changes
    onFilterChange({
      storeId: selectedStore ? Number(selectedStore) : undefined,
      category: selectedCategory || undefined,
    });
  }, [selectedStore, selectedCategory, onFilterChange]);

  return (
    <div className="flex items-center space-x-4 p-4 bg-white rounded-lg shadow-sm">
      <Select value={selectedStore} onValueChange={setSelectedStore}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Stores" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="">All Stores</SelectItem>
          {stores.map((store) => (
            <SelectItem key={store.id} value={String(store.id)}>
              {store.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={selectedCategory} onValueChange={setSelectedCategory}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Categories" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="">All Categories</SelectItem>
          <SelectItem value="A">Category A</SelectItem>
          <SelectItem value="B">Category B</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}