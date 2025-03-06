import axios from 'axios';

// Create axios instance with base URL and common settings
const apiClient = axios.create({
  baseURL: '/api', // Use the proxy path instead of direct backend URL
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add request interceptor to handle loading indicators
apiClient.interceptors.request.use(
  (config) => {
    document.body.classList.add('api-loading');
    return config;
  },
  (error) => {
    document.body.classList.remove('api-loading');
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and loading indicators
apiClient.interceptors.response.use(
  (response) => {
    document.body.classList.remove('api-loading');
    return response.data;
  },
  (error) => {
    document.body.classList.remove('api-loading');
    
    const errorResponse = {
      success: false,
      error: {
        message: 'An unexpected error occurred',
        status: 500,
        details: null
      }
    };
    
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      errorResponse.error.message = error.response.data?.message || 'Server error';
      errorResponse.error.status = error.response.status;
      errorResponse.error.details = error.response.data?.details || null;
    } else if (error.request) {
      // The request was made but no response was received
      errorResponse.error.message = 'No response from server';
      errorResponse.error.status = 0;
    }
    
    return Promise.reject(errorResponse.error);
  }
);

export default apiClient; 