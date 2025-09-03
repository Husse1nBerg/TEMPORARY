// Barrel file for exporting all types

export * from './api';
export * from './price';
export * from './product';
export * from './store';

// You can also add User types here for consistency
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
}