// Use XMLHttpRequest to bypass Mixed Content issues with fetch
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json'
  };
};

export const xhr = (endpoint, options = {}) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const method = options.method || 'GET';
    const url = endpoint.startsWith('http') ? endpoint : endpoint;
    
    console.log('[XHR] Request:', method, url);
    
    xhr.open(method, url, true);
    
    // Set headers
    const headers = { ...getAuthHeaders(), ...(options.headers || {}) };
    Object.keys(headers).forEach(key => {
      if (headers[key]) {
        xhr.setRequestHeader(key, headers[key]);
      }
    });
    
    xhr.onload = function() {
      console.log('[XHR] Response:', xhr.status, url);
      
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          resolve(data);
        } catch (e) {
          resolve(xhr.responseText);
        }
      } else {
        if (xhr.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        reject(new Error(`Request failed: ${xhr.status}`));
      }
    };
    
    xhr.onerror = function() {
      console.error('[XHR] Error:', url);
      reject(new Error('Network error'));
    };
    
    if (options.body) {
      xhr.send(options.body);
    } else {
      xhr.send();
    }
  });
};

export const xhrApi = {
  get: (endpoint) => xhr(endpoint, { method: 'GET' }),
  post: (endpoint, data) => xhr(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => xhr(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint) => xhr(endpoint, { method: 'DELETE' })
};
