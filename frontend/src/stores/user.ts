/**
 * User Store
 * 
 * Manages user authentication state and profile data using Pinia.
 * Handles login, registration, logout, and token management.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { User, LoginCredentials, RegisterData } from '@/types'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)
  const username = computed(() => user.value?.username || '')
  const email = computed(() => user.value?.email || '')

  /**
   * Initialize store from localStorage
   */
  function init() {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      accessToken.value = storedToken
      refreshToken.value = storedRefreshToken
      user.value = JSON.parse(storedUser)
    }
  }

  /**
   * Login with username and password
   */
  async function login(credentials: LoginCredentials): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.login(credentials)
      
      // Store tokens and user data
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user

      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Register new user account
   */
  async function register(data: RegisterData): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.register(data)
      
      // Store tokens and user data
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user

      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Registration failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout and clear authentication data
   */
  async function logout() {
    try {
      await api.logout()
    } catch {
      // Ignore logout errors
    } finally {
      // Clear state
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      error.value = null

      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  /**
   * Fetch current user profile from API
   */
  async function fetchCurrentUser(): Promise<boolean> {
    if (!accessToken.value) return false

    isLoading.value = true
    error.value = null

    try {
      const userData = await api.getCurrentUser()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch user'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // Computed
    isAuthenticated,
    username,
    email,
    
    // Actions
    init,
    login,
    register,
    logout,
    fetchCurrentUser,
    clearError
  }
})
