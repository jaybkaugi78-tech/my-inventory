import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Forward /inventory requests straight through to the Flask API,
    // so the React app can call fetch("/inventory") with no CORS setup
    // needed on the Flask side. Flask must be running on :5000.
    proxy: {
      '/inventory': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
