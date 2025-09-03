// This file contains constant values used throughout the application.

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws';

export const TOKEN_KEY = 'authToken';

export const STORE_CATEGORIES = {
    A: 'Category A',
    B: 'Category B',
};

export const DEFAULT_PAGE_SIZE = 20;