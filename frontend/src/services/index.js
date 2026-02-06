import api from './api';

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
};

export const factionsService = {
  getAll: async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${window.location.origin}/api/factions`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await handleResponse(response);
    return { data };
  },
  getByCode: async (code) => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${window.location.origin}/api/factions/${code}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await handleResponse(response);
    return { data };
  },
  initialize: () => api.post('/factions/initialize')
};

export const departmentsService = {
  getByFaction: (factionCode) => api.get(`/departments/faction/${factionCode}`),
  create: (factionCode, data) => api.post(`/departments/faction/${factionCode}`, data),
  update: (departmentId, data) => api.put(`/departments/${departmentId}`, data),
  delete: (departmentId) => api.delete(`/departments/${departmentId}`)
};

export const weeksService = {
  getByDepartment: (departmentId) => api.get(`/weeks/department/${departmentId}`),
  getCurrent: (departmentId) => api.get(`/weeks/department/${departmentId}/current`),
  getTableData: (weekId) => api.get(`/weeks/${weekId}/table-data`),
  updateTableData: (weekId, data) => api.put(`/weeks/${weekId}/table-data`, data)
};

export const topicsService = {
  getLectures: (factionCode) => api.get(`/topics/lectures/faction/${factionCode}`),
  createLecture: (factionCode, data) => api.post(`/topics/lectures/faction/${factionCode}`, data),
  deleteLecture: (topicId) => api.delete(`/topics/lectures/${topicId}`),
  
  getTrainings: (factionCode) => api.get(`/topics/trainings/faction/${factionCode}`),
  createTraining: (factionCode, data) => api.post(`/topics/trainings/faction/${factionCode}`, data),
  deleteTraining: (topicId) => api.delete(`/topics/trainings/${topicId}`)
};

export const notificationsService = {
  getAll: (unreadOnly = false) => api.get('/notifications', { params: { unread_only: unreadOnly } }),
  markAsRead: (notificationId) => api.post(`/notifications/${notificationId}/read`),
  markAllAsRead: () => api.post('/notifications/read-all')
};

export const auditService = {
  getLogs: (params) => api.get('/audit/logs', { params })
};
