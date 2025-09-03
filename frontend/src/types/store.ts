// Type definitions for Store data
// Corresponds to backend/app/schemas/store.py

export interface Store {
  id: number;
  name: string;
  url: string;
  type?: string;
  scraper_class: string;
  is_active: boolean;
  status: 'idle' | 'scraping' | 'online' | 'offline';
  last_scraped?: string; // ISO date string
  total_products?: number;
  available_products?: number;
  created_at: string; // ISO date string
  updated_at?: string; // ISO date string
}