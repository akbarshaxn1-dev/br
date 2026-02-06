// Force HTTPS API calls
const getBaseUrl = () => {
  const protocol = 'https:';
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}`;
};

export const apiFetch = async (endpoint, options = {}) => {
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}${endpoint}`;
  
  console.log('[apiFetch] Making request to:', url);
  
  const token = localStorage.getItem('access_token');
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...(options.headers || {})
    }
  };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
      throw new Error(`API request failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[apiFetch] Error:', error);
    throw error;
  }
};
