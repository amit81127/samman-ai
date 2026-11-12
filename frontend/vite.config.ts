import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_BACKEND_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    build: {
      target: 'esnext',
      sourcemap: false,
      chunkSizeWarningLimit: 600,
      rollupOptions: {
        output: {
          manualChunks(id: string) {
            const normalized = id.replace(/\\/g, '/')
            if (normalized.includes('/node_modules/')) {
              if (normalized.includes('/node_modules/lucide-react/')) {
                return 'vendor-icons'
              }
              if (normalized.includes('/node_modules/framer-motion/')) {
                return 'vendor-framer'
              }
              if (
                normalized.includes('/node_modules/react-router/') ||
                normalized.includes('/node_modules/react-router-dom/')
              ) {
                return 'vendor-router'
              }
              if (
                normalized.includes('/node_modules/react/') ||
                normalized.includes('/node_modules/react-dom/') ||
                normalized.includes('/node_modules/scheduler/')
              ) {
                return 'vendor-react'
              }
            }
          },
        },
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
      },
    },
  }
})
