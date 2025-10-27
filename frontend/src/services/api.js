import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  verify: () => api.post('/auth/verify'),
};

export const employeeAPI = {
  getAllEmployees: () => api.get('/attendance/employees'),
};

export const attendanceAPI = {
  getCurrentStatus: () => api.get('/attendance/current-status'),
  getDailyAttendance: (date) => api.get(`/attendance/daily?date=${date}`),
  getEmployeeAttendance: (username, startDate, endDate) => 
    api.get(`/attendance/employee/${username}?start_date=${startDate}&end_date=${endDate}`),
  getSummary: (startDate, endDate) => 
    api.get(`/attendance/summary?start_date=${startDate}&end_date=${endDate}`),
  updateRecord: (recordId, data) => api.put(`/attendance/update/${recordId}`, data),
};

export default api;