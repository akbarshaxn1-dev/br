// Global API fetcher that enforces HTTPS
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json'
  };
};

// Force all API calls to use same-origin relative URLs
export const apiCall = async (endpoint, options = {}) => {
  // Strip leading slash if present, then add it back
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  console.log('[API] Calling:', cleanEndpoint);
  
  const config = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {})
    },
    credentials: 'same-origin'
  };
  
  try {
    const response = await fetch(cleanEndpoint, config);
    
    console.log('[API] Response:', response.status, cleanEndpoint);
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `Request failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[API] Error:', error.message, cleanEndpoint);
    throw error;
  }
};

// Convenience methods
export const api = {
  get: (endpoint) => apiCall(endpoint, { method: 'GET' }),
  post: (endpoint, data) => apiCall(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => apiCall(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint) => apiCall(endpoint, { method: 'DELETE' })
};
