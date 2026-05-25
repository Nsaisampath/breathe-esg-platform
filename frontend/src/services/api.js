import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Records API
export const recordsAPI = {
  list: (params) => api.get('/records/', { params }),
  detail: (id) => api.get(`/records/${id}/`),
  summary: (companyId) => api.get('/records/summary/', { params: { company_id: companyId } }),
  approve: (id, data) => api.post(`/records/${id}/approve/`, data),
};

// Uploads API
export const uploadsAPI = {
  uploadSAP: (data) => api.post('/uploads/sap/', data),
  uploadUtility: (data) => api.post('/uploads/utility/', data),
  uploadTravel: (data) => api.post('/uploads/travel/', data),
};
