const API_URL = window.location.origin;

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

const handleResponse = async (response) => {
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
};

export const factionsService = {
  getAll: async () => {
    const response = await fetch(`${API_URL}/api/factions`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  getByCode: async (code) => {
    const response = await fetch(`${API_URL}/api/factions/${code}`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  initialize: async () => {
    const response = await fetch(`${API_URL}/api/factions/initialize`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  }
};

export const departmentsService = {
  getByFaction: async (factionCode) => {
    const response = await fetch(`${API_URL}/api/departments/faction/${factionCode}`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  create: async (factionCode, departmentData) => {
    const response = await fetch(`${API_URL}/api/departments/faction/${factionCode}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'same-origin',
      body: JSON.stringify(departmentData)
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  update: async (departmentId, departmentData) => {
    const response = await fetch(`${API_URL}/api/departments/${departmentId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      credentials: 'same-origin',
      body: JSON.stringify(departmentData)
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  delete: async (departmentId) => {
    const response = await fetch(`${API_URL}/api/departments/${departmentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  }
};

export const weeksService = {
  getByDepartment: async (departmentId) => {
    const response = await fetch(`${API_URL}/api/weeks/department/${departmentId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  getCurrent: async (departmentId) => {
    const response = await fetch(`${API_URL}/api/weeks/department/${departmentId}/current`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  getTableData: async (weekId) => {
    const response = await fetch(`${API_URL}/api/weeks/${weekId}/table-data`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  updateTableData: async (weekId, tableData) => {
    const response = await fetch(`${API_URL}/api/weeks/${weekId}/table-data`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      credentials: 'same-origin',
      body: JSON.stringify(tableData)
    });
    const data = await handleResponse(response);
    return { data };
  }
};

export const topicsService = {
  getLectures: async (factionCode) => {
    const response = await fetch(`${API_URL}/api/topics/lectures/faction/${factionCode}`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  createLecture: async (factionCode, topicData) => {
    const response = await fetch(`${API_URL}/api/topics/lectures/faction/${factionCode}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'same-origin',
      body: JSON.stringify(topicData)
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  deleteLecture: async (topicId) => {
    const response = await fetch(`${API_URL}/api/topics/lectures/${topicId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  getTrainings: async (factionCode) => {
    const response = await fetch(`${API_URL}/api/topics/trainings/faction/${factionCode}`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  createTraining: async (factionCode, topicData) => {
    const response = await fetch(`${API_URL}/api/topics/trainings/faction/${factionCode}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'same-origin',
      body: JSON.stringify(topicData)
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  deleteTraining: async (topicId) => {
    const response = await fetch(`${API_URL}/api/topics/trainings/${topicId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  }
};

export const notificationsService = {
  getAll: async (unreadOnly = false) => {
    const url = `${API_URL}/api/notifications?unread_only=${unreadOnly}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  markAsRead: async (notificationId) => {
    const response = await fetch(`${API_URL}/api/notifications/${notificationId}/read`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  },
  
  markAllAsRead: async () => {
    const response = await fetch(`${API_URL}/api/notifications/read-all`, {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  }
};

export const auditService = {
  getLogs: async (params) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API_URL}/api/audit/logs?${queryString}`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'same-origin'
    });
    const data = await handleResponse(response);
    return { data };
  }
};
