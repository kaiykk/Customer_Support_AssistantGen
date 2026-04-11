/**
 * Vue Router Configuration
 *
 * Defines application routes and navigation guards.
 */

import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      // Catch-all route for 404
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

export default router
