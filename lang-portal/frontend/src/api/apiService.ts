import apiClient from './client';

// Generic API service with common methods
const apiService = {
  get: async <T>(url: string, params = {}): Promise<T> => {
    return apiClient.get(url, { params });
  },
  
  post: async <T>(url: string, data = {}): Promise<T> => {
    return apiClient.post(url, data);
  },
  
  put: async <T>(url: string, data = {}): Promise<T> => {
    return apiClient.put(url, data);
  },
  
  delete: async <T>(url: string): Promise<T> => {
    return apiClient.delete(url);
  }
};

export default apiService; 