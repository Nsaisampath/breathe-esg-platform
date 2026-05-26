import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Records API
export const recordsAPI = {
  list: (params) => api.get('/api/records/', { params }),
  detail: (id) => api.get(`/api/records/${id}/`),
  summary: (companyId) => api.get('/api/records/summary/', { params: { company_id: companyId } }),
  approve: (id, data) => api.post(`/api/records/${id}/approve/`, data),
};

// Uploads API
export const uploadsAPI = {
  uploadSAP: (data) => api.post('/api/uploads/sap/', data),
  uploadUtility: (data) => api.post('/api/uploads/utility/', data),
  uploadTravel: (data) => api.post('/api/uploads/travel/', data),
};
