// Generic type definitions for API interactions

export interface ApiErrorResponse {
  error: string;
  details?: string | any;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}