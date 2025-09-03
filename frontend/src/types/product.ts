// Type definitions for Product data
// Corresponds to backend/app/schemas/product.py

export interface Product {
  id: number;
  name: string;
  category: string; // "A" or "B"
  keywords: string[];
  description?: string;
  is_organic: boolean;
  is_active: boolean;
  created_at: string; // ISO date string
  updated_at?: string; // ISO date string
}