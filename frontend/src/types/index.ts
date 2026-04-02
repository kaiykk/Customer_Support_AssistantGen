/**
 * TypeScript Type Definitions
 * 
 * Centralized type definitions for the AssistGen frontend application.
 * Provides type safety and IntelliSense support across the application.
 */

/**
 * User-related types
 */
export interface User {
  id: number
  username: string
  email: string
  created_at: string
  updated_at?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

/**
 * Conversation-related types
 */
export enum DialogueType {
  NORMAL = 'normal',
  DEEP_THINKING = 'deep_thinking',
  WEB_SEARCH = 'web_search',
  RAG = 'rag'
}

export interface Conversation {
  id: number
  user_id: number
  title: string
  dialogue_type: DialogueType
  status: 'active' | 'archived' | 'completed'
  created_at: string
  updated_at?: string
  message_count?: number
  last_message_time?: string
}

/**
 * Message-related types
 */
export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
  metadata?: Record<string, any>
}

/**
 * Chat request/response types
 */
export interface ChatRequest {
  message: string
  conversation_id?: number
  dialogue_type?: DialogueType
  stream?: boolean
}

export interface ChatResponse {
  message: Message
  conversation_id: number
}

/**
 * API response wrapper
 */
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

/**
 * UI state types
 */
export interface LoadingState {
  isLoading: boolean
  message?: string
}

export interface ErrorState {
  hasError: boolean
  message?: string
  code?: string
}
