/**
 * Vue Router Configuration
 * 
 * Defines application routes and navigation guards.
 * Handles authentication-based route protection.
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: Login,
      meta: { requiresAuth: false }
    },
    {
      // Catch-all route for 404
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

/**
 * Navigation guard: Check authentication before route access
 */
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !userStore.isAuthenticated) {
    // Redirect to login if authentication required
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && userStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    // Redirect to home if already authenticated and trying to access login/register
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
