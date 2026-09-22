import { defineApplicationConfig } from '@vben/vite-config';

export default defineApplicationConfig({
  overrides: {
    optimizeDeps: {
      include: [
        'echarts/core',
        'echarts/charts',
        'echarts/components',
        'echarts/renderers',
        'qrcode',
        '@iconify/iconify',
        'ant-design-vue/es/locale/zh_CN',
        'ant-design-vue/es/locale/en_US',
      ],
    },
    server: {
      port: 8082,
      host: '0.0.0.0',
      open: false,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          ws: true,
        },
      },
      warmup: {
        clientFiles: ['./index.html', './src/{views,components}/*'],
      },
    },
    plugins: [
      {
        name: 'api-proxy-middleware',
        configureServer(server) {
          server.middlewares.use((req, res, next) => {
            if (req.url && req.url.startsWith('/api')) {
              const http = require('http');
              const proxyReq = http.request({
                hostname: 'localhost',
                port: 8000,
                path: req.url,
                method: req.method || 'GET',
                headers: { ...req.headers, host: 'localhost:8000' },
              }, (proxyRes) => {
                res.writeHead(proxyRes.statusCode || 200, proxyRes.headers);
                proxyRes.pipe(res);
              });
              proxyReq.on('error', () => {
                res.statusCode = 502;
                res.end('Bad Gateway');
              });
              req.pipe(proxyReq);
            } else {
              next();
            }
          });
        },
      },
    ],
  },
});
