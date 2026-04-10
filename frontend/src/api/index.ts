/**
 * API Client Module
 * 
 * Centralized HTTP client for communicating with the AssistGen backend API.
 * Handles authentication, request/response interceptors, and error handling.
 */

import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type {
  User,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  Conversation,
  Message,
  ChatRequest,
  ChatResponse
} from '@/types'
import { DialogueType } from '@/types'

/**
 * API client instance with configured base URL and interceptors
 */
class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  /**
   * Configure request and response interceptors
   */
  private setupInterceptors() {
    // Request interceptor: Add auth token to requests
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor: Handle common errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              const response = await this.refreshToken(refreshToken)
              localStorage.setItem('access_token', response.access_token)
              localStorage.setItem('refresh_token', response.refresh_token)
              
              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${response.access_token}`
                return this.client.request(error.config)
              }
            } catch {
              // Refresh failed, clear tokens and redirect to login
              this.clearAuth()
              window.location.href = '/login'
            }
          } else {
            this.clearAuth()
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  /**
   * Clear authentication data from storage
   */
  private clearAuth() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // ==================== Authentication APIs ====================

  /**
   * User login
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', credentials)
    return response.data
  }

  /**
   * User registration
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', data)
    return response.data
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  }

  /**
   * User logout
   */
  async logout(): Promise<void> {
    await this.client.post('/auth/logout')
    this.clearAuth()
  }

  // ==================== User APIs ====================

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/users/me')
    return response.data
  }

  /**
   * Update user profile
   */
  async updateUser(userId: number, data: Partial<User>): Promise<User> {
    const response = await this.client.put<User>(`/users/${userId}`, data)
    return response.data
  }

  // ==================== Conversation APIs ====================

  /**
   * Get all conversations for current user
   */
  async getConversations(): Promise<Conversation[]> {
    const response = await this.client.get<Conversation[]>('/conversations')
    return response.data
  }

  /**
   * Get a specific conversation by ID
   */
  async getConversation(conversationId: number): Promise<Conversation> {
    const response = await this.client.get<Conversation>(`/conversations/${conversationId}`)
    return response.data
  }

  /**
   * Create a new conversation
   */
  async createConversation(title: string, dialogueType: DialogueType = DialogueType.NORMAL): Promise<Conversation> {
    const response = await this.client.post<Conversation>('/conversations', {
      title,
      dialogue_type: dialogueType
    })
    return response.data
  }

  /**
   * Update conversation details
   */
  async updateConversation(conversationId: number, data: Partial<Conversation>): Promise<Conversation> {
    const response = await this.client.put<Conversation>(`/conversations/${conversationId}`, data)
    return response.data
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: number): Promise<void> {
    await this.client.delete(`/conversations/${conversationId}`)
  }

  // ==================== Message APIs ====================

  /**
   * Get all messages in a conversation
   */
  async getMessages(conversationId: number): Promise<Message[]> {
    const response = await this.client.get<Message[]>(`/conversations/${conversationId}/messages`)
    return response.data
  }

  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/chat', request)
    return response.data
  }

  /**
   * Send a chat message with streaming response
   */
  async sendMessageStream(request: ChatRequest, onChunk: (chunk: string) => void): Promise<void> {
    const response = await this.client.post('/chat/stream', request, {
      responseType: 'stream',
      adapter: 'fetch'
    })

    const reader = response.data.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') return
          
          try {
            const parsed = JSON.parse(data)
            onChunk(parsed.content || '')
          } catch {
            // Ignore parse errors
          }
        }
      }
    }
  }
}

// Export singleton instance
export const api = new ApiClient()
export default api
