import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 개발 서버 설정
  server: {
    port: 3000,
    host: true,
    strictPort: false, // 포트가 사용 중이면 다른 포트 사용
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
  
  // 빌드 설정
  build: {
    outDir: 'dist',
    sourcemap: true,
    // 빌드 시 경고를 오류로 처리하지 않음
    rollupOptions: {
      onwarn(warning, warn) {
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE') {
          return
        }
        warn(warning)
      }
    }
  },
  
  // 별칭 설정
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@types': resolve(__dirname, 'src/types'),
      '@utils': resolve(__dirname, 'src/utils'),
    },
  },
  
  // 환경 변수 설정
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
  },
  
  // ESBuild 최적화
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  },
})
