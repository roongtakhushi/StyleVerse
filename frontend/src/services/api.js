import axios from 'axios';

// Resilient API base URL normalization (handles trailing slashes, missing /api prefix, etc.)
const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const cleanBase = rawBase.trim().replace(/\/+$/, '');
const API_BASE_URL = cleanBase.endsWith('/api') ? cleanBase : `${cleanBase}/api`;

const rawImageBase = import.meta.env.VITE_IMAGE_BASE_URL || cleanBase.replace(/\/api$/, '') || 'http://localhost:8000';
export const IMAGE_BASE_URL = rawImageBase.trim().replace(/\/+$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000, // 45s timeout to gracefully accommodate Render cold starts
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('styleverse_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token expiry / unauthorized responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if expired or invalid
      localStorage.removeItem('styleverse_token');
      localStorage.removeItem('styleverse_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

