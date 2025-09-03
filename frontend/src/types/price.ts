// Type definitions for Price data
// Corresponds to backend/app/schemas/price.py

export interface Price {
  id: number;
  product_id: number;
  store_id: number;
  price: number;
  original_price?: number;
  price_per_kg?: number;
  pack_size?: string;
  pack_unit?: string;
  is_available: boolean;
  is_discounted: boolean;
  product_url?: string;
  image_url?: string;
  
  // Joined fields from the API response
  product_name?: string;
  store_name?: string;
  price_change?: number;
  price_change_percent?: number;
  
  scraped_at: string; // ISO date string
  created_at: string; // ISO date string
  updated_at?: string; // ISO date string
}

export interface PriceTrend {
    date: string;
    store_id: number;
    price: number;
    price_per_kg?: number;
    is_available: boolean;
}