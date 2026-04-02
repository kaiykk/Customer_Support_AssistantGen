/**
 * Application Entry Point
 * 
 * This file initializes the Vue application with all necessary plugins
 * and configurations including router, state management, and global styles.
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import global styles
import './styles/main.scss'

// Create Vue application instance
const app = createApp(App)

// Create Pinia store instance
const pinia = createPinia()

// Register plugins
app.use(pinia)
app.use(router)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Error info:', info)
  // TODO: Send to error tracking service
}

// Mount application
app.mount('#app')
