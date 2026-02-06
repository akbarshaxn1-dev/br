const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy all /api requests to backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
      secure: false,
      logLevel: 'info',
      onProxyReq: (proxyReq, req, res) => {
        console.log('[Proxy] Proxying:', req.method, req.url, '-> http://localhost:8001');
      },
      onError: (err, req, res) => {
        console.error('[Proxy] Error:', err.message);
      }
    })
  );
  
  console.log('[Proxy] Setup complete - /api/* -> http://localhost:8001');
};
