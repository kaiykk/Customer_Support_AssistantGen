/**
 * Conversation Store
 * 
 * Manages conversation and message state using Pinia.
 * Handles conversation creation, message sending, and chat history.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { Conversation, Message, ChatRequest, DialogueType } from '@/types'

export const useConversationStore = defineStore('conversation', () => {
  // State
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isSending = ref(false)
  const isTyping = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasConversations = computed(() => conversations.value.length > 0)
  const currentConversationId = computed(() => currentConversation.value?.id)
  const sortedConversations = computed(() => 
    [...conversations.value].sort((a, b) => 
      new Date(b.updated_at || b.created_at).getTime() - 
      new Date(a.updated_at || a.created_at).getTime()
    )
  )

  /**
   * Fetch all conversations for current user
   */
  async function fetchConversations(): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      conversations.value = await api.getConversations()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch conversations'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new conversation
   */
  async function createConversation(title: string, dialogueType: DialogueType): Promise<Conversation | null> {
    isLoading.value = true
    error.value = null

    try {
      const conversation = await api.createConversation(title, dialogueType)
      conversations.value.unshift(conversation)
      currentConversation.value = conversation
      messages.value = []
      return conversation
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create conversation'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Select a conversation and load its messages
   */
  async function selectConversation(conversationId: number): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const conversation = await api.getConversation(conversationId)
      const conversationMessages = await api.getMessages(conversationId)
      
      currentConversation.value = conversation
      messages.value = conversationMessages
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load conversation'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Send a message in the current conversation
   */
  async function sendMessage(content: string, dialogueType?: DialogueType): Promise<boolean> {
    if (!content.trim()) return false

    isSending.value = true
    isTyping.value = true
    error.value = null

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now(), // Temporary ID
      conversation_id: currentConversation.value?.id || 0,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)

    try {
      const request: ChatRequest = {
        message: content,
        conversation_id: currentConversation.value?.id,
        dialogue_type: dialogueType || currentConversation.value?.dialogue_type
      }

      const response = await api.sendMessage(request)
      
      // Update conversation ID if this was the first message
      if (!currentConversation.value) {
        currentConversation.value = {
          id: response.conversation_id,
          user_id: 0,
          title: content.slice(0, 50),
          dialogue_type: dialogueType || 'normal',
          status: 'active',
          created_at: new Date().toISOString()
        }
        conversations.value.unshift(currentConversation.value)
      }

      // Replace temporary user message with actual one
      messages.value[messages.value.length - 1] = response.message

      // Add assistant response
      messages.value.push(response.message)

      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to send message'
      // Remove temporary user message on error
      messages.value.pop()
      return false
    } finally {
      isSending.value = false
      isTyping.value = false
    }
  }

  /**
   * Delete a conversation
   */
  async function deleteConversation(conversationId: number): Promise<boolean> {
    error.value = null

    try {
      await api.deleteConversation(conversationId)
      
      // Remove from list
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      
      // Clear current conversation if it was deleted
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = null
        messages.value = []
      }

      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete conversation'
      return false
    }
  }

  /**
   * Start a new conversation (clear current state)
   */
  function startNewConversation() {
    currentConversation.value = null
    messages.value = []
    error.value = null
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null
  }

  /**
   * Clear all state (on logout)
   */
  function clearAll() {
    conversations.value = []
    currentConversation.value = null
    messages.value = []
    isLoading.value = false
    isSending.value = false
    isTyping.value = false
    error.value = null
  }

  return {
    // State
    conversations,
    currentConversation,
    messages,
    isLoading,
    isSending,
    isTyping,
    error,
    
    // Computed
    hasConversations,
    currentConversationId,
    sortedConversations,
    
    // Actions
    fetchConversations,
    createConversation,
    selectConversation,
    sendMessage,
    deleteConversation,
    startNewConversation,
    clearError,
    clearAll
  }
})
