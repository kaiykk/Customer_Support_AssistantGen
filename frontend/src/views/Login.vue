<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Logo -->
      <div class="logo-section">
        <div class="logo-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <path d="M24 4L40 14V34L24 44L8 34V14L24 4Z" fill="#4b4bff" opacity="0.2"/>
            <path d="M24 4L40 14V34L24 44L8 34V14L24 4Z" stroke="#4b4bff" stroke-width="2"/>
            <circle cx="24" cy="24" r="8" fill="#4b4bff" opacity="0.2" stroke="#4b4bff" stroke-width="2"/>
          </svg>
        </div>
        <h1 class="logo-title">AssistGen</h1>
        <p class="logo-subtitle">Intelligent Customer Service</p>
      </div>

      <!-- Tab Switcher -->
      <div class="tab-switcher">
        <button 
          :class="['tab-btn', { active: activeTab === 'login' }]"
          @click="activeTab = 'login'"
          aria-label="Switch to login"
        >
          Login
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'register' }]"
          @click="activeTab = 'register'"
          aria-label="Switch to register"
        >
          Register
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="error-banner" role="alert">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/>
          <path d="M8 4V8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="8" cy="11" r="0.5" fill="currentColor"/>
        </svg>
        {{ errorMessage }}
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="login-email">Email</label>
          <input
            id="login-email"
            v-model="loginForm.email"
            type="email"
            placeholder="Enter your email"
            required
            aria-required="true"
          />
        </div>

        <div class="form-group">
          <label for="login-password">Password</label>
          <input
            id="login-password"
            v-model="loginForm.password"
            type="password"
            placeholder="Enter your password"
            required
            aria-required="true"
          />
        </div>

        <button 
          type="submit" 
          class="submit-btn"
          :disabled="userStore.isLoading"
          :aria-busy="userStore.isLoading"
        >
          <span v-if="!userStore.isLoading">Login</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <!-- Register Form -->
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="register-username">Username</label>
          <input
            id="register-username"
            v-model="registerForm.username"
            type="text"
            placeholder="Choose a username"
            required
            aria-required="true"
            minlength="3"
            maxlength="50"
          />
        </div>

        <div class="form-group">
          <label for="register-email">Email</label>
          <input
            id="register-email"
            v-model="registerForm.email"
            type="email"
            placeholder="Enter your email"
            required
            aria-required="true"
          />
        </div>

        <div class="form-group">
          <label for="register-password">Password</label>
          <input
            id="register-password"
            v-model="registerForm.password"
            type="password"
            placeholder="Create a password (min 8 characters)"
            required
            aria-required="true"
            minlength="8"
          />
        </div>

        <button 
          type="submit" 
          class="submit-btn"
          :disabled="userStore.isLoading"
          :aria-busy="userStore.isLoading"
        >
          <span v-if="!userStore.isLoading">Register</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </form>

      <!-- Footer -->
      <div class="form-footer">
        <p class="footer-text">
          By continuing, you agree to our 
          <a href="#" @click.prevent>Terms of Service</a> and 
          <a href="#" @click.prevent>Privacy Policy</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref<'login' | 'register'>('login')
const errorMessage = ref('')

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  errorMessage.value = ''

  const success = await userStore.login({
    username: loginForm.value.email,
    password: loginForm.value.password
  })

  if (success) {
    router.push('/')
  } else {
    errorMessage.value = userStore.error || 'Login failed. Please try again.'
  }
}

const handleRegister = async () => {
  errorMessage.value = ''

  const success = await userStore.register({
    username: registerForm.value.username,
    email: registerForm.value.email,
    password: registerForm.value.password
  })

  if (success) {
    router.push('/')
  } else {
    errorMessage.value = userStore.error || 'Registration failed. Please try again.'
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  padding: var(--spacing-md);
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-xxl);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.logo-section {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo-icon {
  margin-bottom: var(--spacing-md);
}

.logo-title {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.logo-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.tab-switcher {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  background: var(--bg-tertiary);
  padding: 4px;
  border-radius: var(--border-radius-md);
}

.tab-btn {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: none;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    color: var(--text-primary);
  }

  &.active {
    background: var(--primary-color);
    color: white;
  }
}

.error-banner {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid var(--danger-color);
  border-radius: var(--border-radius-md);
  color: var(--danger-color);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-lg);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);

  label {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  input {
    padding: var(--spacing-md);
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    color: var(--text-primary);
    font-size: var(--font-size-md);
    transition: all var(--transition-fast);

    &::placeholder {
      color: var(--text-tertiary);
    }

    &:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 3px rgba(75, 75, 255, 0.1);
    }

    &:hover {
      border-color: var(--border-hover);
    }
  }
}

.submit-btn {
  padding: var(--spacing-md);
  background: var(--primary-color);
  border: none;
  border-radius: var(--border-radius-md);
  color: white;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover:not(:disabled) {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(75, 75, 255, 0.3);
  }

  &:active:not(:disabled) {
    background: var(--primary-active);
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  margin-top: var(--spacing-lg);
  text-align: center;
}

.footer-text {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);

  a {
    color: var(--primary-color);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

// Responsive design
@media (max-width: 480px) {
  .login-card {
    padding: var(--spacing-lg);
  }

  .logo-title {
    font-size: var(--font-size-xl);
  }
}
</style>
