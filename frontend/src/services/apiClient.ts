import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import toast from 'react-hot-toast';

// Base URL configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: any) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: any) => {
    // Calculate request duration
    const duration = new Date().getTime() - (response.config.metadata?.startTime?.getTime() || new Date().getTime());
    console.debug(`API Request: ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);

    return response.data;
  },
  (error: any) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const message = (error.response.data as any)?.message || (error.response.data as any)?.detail || 'An error occurred';

      switch (status) {
        case 401:
          // Unauthorized - redirect to login or refresh token
          localStorage.removeItem('auth_token');
          toast.error('Session expired. Please log in again.');
          // Redirect to login if needed
          break;
        case 403:
          toast.error('Access denied');
          break;
        case 404:
          toast.error('Resource not found');
          break;
        case 422:
          // Validation errors
          if (error.response.data?.errors) {
            const errors = error.response.data.errors;
            errors.forEach((err: any) => {
              toast.error(`${err.field}: ${err.message}`);
            });
          } else {
            toast.error(message);
          }
          break;
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
        case 500:
          toast.error('Server error. Please try again later.');
          break;
        default:
          toast.error(message);
      }

      return Promise.reject({
        status,
        message,
        data: error.response.data,
      });
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.');
      return Promise.reject({
        status: 0,
        message: 'Network error',
        data: null,
      });
    } else {
      // Request setup error
      toast.error('Request failed to send');
      return Promise.reject({
        status: 0,
        message: error.message,
        data: null,
      });
    }
  }
);

// API methods
export const api = {
  // Generic methods
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.get(url, config),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.post(url, data, config),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.put(url, data, config),

  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.patch(url, data, config),

  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.delete(url, config),

  // File upload method
  upload: <T = any>(
    url: string,
    file: File,
    options?: {
      onUploadProgress?: (progressEvent: any) => void;
      additionalData?: Record<string, any>;
    }
  ): Promise<T> => {
    const formData = new FormData();
    formData.append('file', file);

    // Add additional data if provided
    if (options?.additionalData) {
      Object.entries(options.additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: options?.onUploadProgress,
    });
  },

  // Download method
  download: (url: string, filename?: string): Promise<void> => {
    return apiClient.get(url, {
      responseType: 'blob',
    }).then((response) => {
      const blob = response instanceof Blob ? response : new Blob([response as any]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    });
  },
};

// Specific API endpoints
export const apiEndpoints = {
  // Auth endpoints
  auth: {
    login: (credentials: { username: string; password: string }) =>
      api.post('/auth/login', credentials),
    
    logout: () =>
      api.post('/auth/logout'),
    
    refresh: () =>
      api.post('/auth/refresh'),
  },

  // File upload endpoints
  files: {
    upload: (file: File, onProgress?: (progress: number) => void) =>
      api.upload('/files/upload', file, {
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      }),

    getById: (id: string) =>
      api.get(`/files/${id}`),

    delete: (id: string) =>
      api.delete(`/files/${id}`),

    download: (id: string, filename?: string) =>
      api.download(`/files/${id}/download`, filename),
  },

  // Task endpoints
  tasks: {
    getAll: (params?: { page?: number; limit?: number; status?: string }) =>
      api.get('/tasks', { params }),

    getById: (id: string) =>
      api.get(`/tasks/${id}`),

    getRecent: (limit: number = 5) =>
      api.get(`/tasks/recent?limit=${limit}`),

    cancel: (id: string) =>
      api.post(`/tasks/${id}/cancel`),

    retry: (id: string) =>
      api.post(`/tasks/${id}/retry`),
  },

  // Results endpoints
  results: {
    getByTaskId: (taskId: string) =>
      api.get(`/results/${taskId}`),

    download: (taskId: string, format: 'json' | 'csv' | 'excel' = 'json') =>
      api.download(`/results/${taskId}/download?format=${format}`, `results-${taskId}.${format}`),
  },

  // Dashboard endpoints
  dashboard: {
    getStats: () =>
      api.get('/dashboard/stats'),

    getMetrics: (timeRange: '1h' | '24h' | '7d' | '30d' = '24h') =>
      api.get(`/dashboard/metrics?range=${timeRange}`),
  },

  // System endpoints
  system: {
    getHealth: () =>
      api.get('/system/health'),

    getStatus: () =>
      api.get('/system/status'),

    getMetrics: () =>
      api.get('/system/metrics'),
  },
};

export default apiClient;
