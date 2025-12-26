// Default to local backend; override via VITE_API_URL when needed
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
