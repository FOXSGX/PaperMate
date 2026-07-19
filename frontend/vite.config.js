import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端默认端口与 backend/.env SERVER_PORT、CORS 保持一致
const DEFAULT_BACKEND = 'http://127.0.0.1:8000'
const DEFAULT_FRONTEND_PORT = 5173

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_BACKEND_URL || DEFAULT_BACKEND
  const frontendPort = Number(env.VITE_PORT || DEFAULT_FRONTEND_PORT)

  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: frontendPort,
      strictPort: true,
      proxy: {
        // REST + SSE
        '/api': {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
        // 排版结果下载
        '/outputs': {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
        // 健康检查（可选，便于前端探测）
        '/health': {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
      },
    },
    preview: {
      host: '0.0.0.0',
      port: 4173,
      proxy: {
        '/api': { target: backendTarget, changeOrigin: true },
        '/outputs': { target: backendTarget, changeOrigin: true },
        '/health': { target: backendTarget, changeOrigin: true },
      },
    },
  }
})
