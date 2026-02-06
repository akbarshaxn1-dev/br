// Runtime configuration
export const getApiUrl = () => {
  // Always use current origin for API calls
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return process.env.REACT_APP_BACKEND_URL || 'https://dept-manager-4.preview.emergentagent.com';
};

export const API_BASE_URL = getApiUrl();
