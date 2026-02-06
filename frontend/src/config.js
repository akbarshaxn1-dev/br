// Runtime configuration
export const getApiUrl = () => {
  // Use runtime config from window
  if (typeof window !== 'undefined' && window.ENV) {
    return window.ENV.API_URL;
  }
  // Fallback to current origin
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'https://dept-manager-4.preview.emergentagent.com';
};

export const API_BASE_URL = getApiUrl();
