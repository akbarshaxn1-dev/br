import api from './api';

export const factionsService = {
  getAll: () => api.get('/factions'),
  getByCode: (code) => api.get(`/factions/${code}`),
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
