import axios from 'axios';

// Resilient API base URL normalization (handles trailing slashes, missing /api prefix, etc.)
const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const cleanBase = rawBase.trim().replace(/\/+$/, '');
const API_BASE_URL = cleanBase.endsWith('/api') ? cleanBase : `${cleanBase}/api`;

const rawImageBase = import.meta.env.VITE_IMAGE_BASE_URL || cleanBase.replace(/\/api$/, '') || 'http://localhost:8000';
export const IMAGE_BASE_URL = rawImageBase.trim().replace(/\/+$/, '');

export const GITHUB_RAW_BASE = "https://raw.githubusercontent.com/roongtakhushi/StyleVerse/main/backend/uploads/";

export const resolveGarmentImageUrl = (imgUrl) => {
  if (!imgUrl) return '/placeholder-garment.svg';
  if (imgUrl.startsWith('http')) return imgUrl;
  const filename = imgUrl.split('/').pop();
  if (filename && (filename.startsWith('studio_pure_') || filename.startsWith('studio_live_'))) {
    // Deliver instantly from Vercel Edge CDN same-origin (Mumbai edge node in India)
    return `/uploads/${filename}`;
  }
  return `${IMAGE_BASE_URL}${imgUrl.startsWith('/') ? imgUrl : `/${imgUrl}`}`;
};

export const handleGarmentImageError = (e, originalUrl) => {
  const currentSrc = e.currentTarget.src || '';
  const fname = (originalUrl || '').split('/').pop();
  
  // 1st fallback: Fastly / GitHub Raw global repository CDN
  if (fname && !currentSrc.includes('raw.githubusercontent.com')) {
    e.currentTarget.src = `${GITHUB_RAW_BASE}${fname}`;
  } else if (fname && !currentSrc.includes('/uploads/')) {
    e.currentTarget.src = `/uploads/${fname}`;
  } else if (!currentSrc.includes('placeholder-garment.svg')) {
    e.currentTarget.src = '/placeholder-garment.svg';
  }
};

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

