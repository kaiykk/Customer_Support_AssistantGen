<template>
  <div class="home-container">
    <!-- Sidebar -->
    <aside 
      class="sidebar" 
      :class="{ collapsed: isSidebarCollapsed }"
      role="navigation"
      aria-label="Conversation history"
    >
      <div class="sidebar-header">
        <h2 class="sidebar-title">AssistGen</h2>
        <button 
          class="new-chat-btn"
          @click="createNewConversation"
          aria-label="Start new conversation"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span>New Chat</span>
        </button>
      </div>

      <div class="conversation-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          :class="['conversation-item', { active: conv.id === currentConversationId }]"
          @click="loadConversation(conv.id)"
          role="button"
          tabindex="0"
          @keydown.enter="loadConversation(conv.id)"
        >
          <div class="conversation-content">
            <span class="conversation-title">{{ conv.title }}</span>
            <span class="conversation-time">{{ formatTime(conv.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <div class="user-avatar">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="10" cy="8" r="3" stroke="currentColor" stroke-width="1.5"/>
              <path d="M15 17C15 14.5 13 13 10 13C7 13 5 14.5 5 17" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </div>
          <span class="user-name">{{ username }}</span>
        </div>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="chat-main">
      <!-- Welcome Screen -->
      <div v-if="!messages.length" class="welcome-screen">
        <div class="welcome-content">
          <h1 class="welcome-title">Welcome to AssistGen</h1>
          <p class="welcome-subtitle">
            I'm your AI assistant. I can help you with coding, writing, and answering questions.
          </p>
          
          <div class="quick-actions">
            <button class="quick-action-btn" @click="setQuickPrompt('Help me write code')">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M6 8L2 12L6 16M14 8L18 12L14 16M12 4L8 20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span>Write Code</span>
            </button>
            <button class="quick-action-btn" @click="setQuickPrompt('Explain this concept')">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.5"/>
                <path d="M10 14V10M10 6H10.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span>Explain</span>
            </button>
            <button class="quick-action-btn" @click="setQuickPrompt('Search the web for')">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/>
                <path d="M14 14L18 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span>Search</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-else class="messages-container" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', `message-${message.role}`]"
        >
          <div class="message-avatar">
            <svg v-if="message.role === 'user'" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="12" cy="9" r="3" stroke="currentColor" stroke-width="1.5"/>
              <path d="M18 20C18 17 16 15 12 15C8 15 6 17 6 20" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L20 7V17L12 22L4 17V7L12 2Z" fill="#4b4bff" opacity="0.2"/>
              <path d="M12 2L20 7V17L12 22L4 17V7L12 2Z" stroke="#4b4bff" stroke-width="1.5"/>
              <circle cx="12" cy="12" r="3" fill="#4b4bff"/>
            </svg>
          </div>
          <div class="message-content" v-html="renderMarkdown(message.content)"></div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isTyping" class="message message-assistant">
          <div class="message-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L20 7V17L12 22L4 17V7L12 2Z" fill="#4b4bff" opacity="0.2"/>
              <path d="M12 2L20 7V17L12 22L4 17V7L12 2Z" stroke="#4b4bff" stroke-width="1.5"/>
              <circle cx="12" cy="12" r="3" fill="#4b4bff"/>
            </svg>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <textarea
            v-model="userInput"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="Send a message to AssistGen..."
            rows="1"
            aria-label="Message input"
            ref="inputTextarea"
          ></textarea>
          
          <div class="input-actions">
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="!userInput.trim() || isTyping"
              aria-label="Send message"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="input-footer">
          <span class="disclaimer">AI-generated content may be inaccurate</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useConversationStore } from '@/stores/conversation'
import { DialogueType } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const conversationStore = useConversationStore()

const isSidebarCollapsed = ref(false)
const showUserMenu = ref(false)
const userInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const inputTextarea = ref<HTMLTextAreaElement | null>(null)

// Computed properties from stores
const messages = computed(() => conversationStore.messages)
const isTyping = computed(() => conversationStore.isTyping)
const currentConversationId = computed(() => conversationStore.currentConversationId)
const conversations = computed(() => conversationStore.sortedConversations)
const username = computed(() => userStore.username || 'User')

// Simple markdown renderer (basic implementation)
const renderMarkdown = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const createNewConversation = () => {
  conversationStore.startNewConversation()
  userInput.value = ''
}

const loadConversation = async (id: number) => {
  await conversationStore.selectConversation(id)
  scrollToBottom()
}

const setQuickPrompt = (prompt: string) => {
  userInput.value = prompt
  inputTextarea.value?.focus()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isTyping.value) return

  const content = userInput.value.trim()
  userInput.value = ''

  await conversationStore.sendMessage(content, DialogueType.NORMAL)
  scrollToBottom()
}

// Auto-resize textarea
watch(userInput, () => {
  if (inputTextarea.value) {
    inputTextarea.value.style.height = 'auto'
    inputTextarea.value.style.height = inputTextarea.value.scrollHeight + 'px'
  }
})

// Watch messages for auto-scroll
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

onMounted(async () => {
  await conversationStore.fetchConversations()
  
  // If no conversations exist, start a new one
  if (!conversationStore.hasConversations) {
    conversationStore.startNewConversation()
  }
})
</script>

<style lang="scss" scoped>
.home-container {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

.sidebar {
  width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);

  &.collapsed {
    width: 0;
    overflow: hidden;
  }
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.sidebar-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--primary-color);
  border: none;
  border-radius: var(--border-radius-md);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    background: var(--primary-hover);
  }
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.conversation-item {
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: var(--spacing-xs);

  &:hover {
    background: var(--bg-hover);
  }

  &.active {
    background: var(--bg-tertiary);
  }
}

.conversation-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.conversation-title {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

.conversation-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.sidebar-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    background: var(--bg-hover);
  }
}

.user-avatar {
  color: var(--text-secondary);
}

.user-name {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.welcome-content {
  text-align: center;
  max-width: 600px;
}

.welcome-title {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.welcome-subtitle {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xl);
}

.quick-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    background: var(--bg-tertiary);
    border-color: var(--primary-color);
    transform: translateY(-2px);
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-xl);
}

.message {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  animation: fadeIn 0.3s ease;

  &.message-user {
    .message-content {
      background: var(--primary-color);
      color: white;
    }
  }

  &.message-assistant {
    .message-content {
      background: var(--bg-secondary);
      color: var(--text-primary);
    }
  }
}

.message-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.message-content {
  flex: 1;
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-md);
  line-height: var(--line-height-relaxed);
  max-width: 70%;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: var(--spacing-sm);

  span {
    width: 8px;
    height: 8px;
    background: var(--text-tertiary);
    border-radius: 50%;
    animation: typing 1.4s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.input-area {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.input-container {
  display: flex;
  gap: var(--spacing-sm);
  align-items: flex-end;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-sm);
  transition: all var(--transition-fast);

  &:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(75, 75, 255, 0.1);
  }

  textarea {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: var(--font-size-md);
    resize: none;
    max-height: 200px;
    padding: var(--spacing-sm);

    &::placeholder {
      color: var(--text-tertiary);
    }

    &:focus {
      outline: none;
    }
  }
}

.input-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.send-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  border: none;
  border-radius: var(--border-radius-md);
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover:not(:disabled) {
    background: var(--primary-hover);
    transform: scale(1.05);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.input-footer {
  margin-top: var(--spacing-sm);
  text-align: center;
}

.disclaimer {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

// Responsive design
@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    z-index: 100;
    height: 100%;

    &.collapsed {
      transform: translateX(-100%);
    }
  }

  .message-content {
    max-width: 85%;
  }
}
</style>
