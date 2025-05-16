import axios from 'axios';

const apiClient = axios.create({
  baseURL: '',
  withCredentials: true, // Important for sending cookies
  headers: {
    'Content-Type': 'application/json'
  }
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Instead of redirecting directly, emit an event that AuthContext can handle
      const event = new CustomEvent('auth-error', {
        detail: { status: 401 }
      });
      window.dispatchEvent(event);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
