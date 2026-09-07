import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND_URL = 'http://127.0.0.1:5000'

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {

      '/login': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/sign_up': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/Add_farm': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/update_farm': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/get_all_farms_of_landlord': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/add_batch': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/farm_location': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/get_landlord_by_id': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/profile': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/predict': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/farm': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/start_batch_session': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/batch_report': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/stop_batch_session': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/all_batch': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/compare_batch': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/best_batch': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/get_temp_records': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/clear_temp': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/predict/images': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/get_notifications': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/update_temp_record': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/save_temp_to_batch': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/start_temp_session': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

      '/batch_images': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
      },

    },
  },
})