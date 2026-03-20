import axios from 'axios';

// Vite env fallback gracefully to local dev proxy
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_URL,
  withCredentials: true, // HTTP Only cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor logic for automatic token refreshing etc.
const AUTH_PATHS = ['/auth/login', '/auth/refresh'];
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // C5: Skip auth endpoints — a failed login (401) must NOT trigger redirect
    if (error.response?.status === 401 && !AUTH_PATHS.some(p => error.config?.url?.includes(p))) {
      window.dispatchEvent(new CustomEvent('auth:expired'));
    }
    return Promise.reject(error);
  }
);

export default client;
