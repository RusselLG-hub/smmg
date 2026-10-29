import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthService } from '~/services/auth'
import type { User } from '~~/shared/types/User'
import type {
  ForgotPasswordRequest,
  LoginRequest,
  RegisterRequest,
  ResetPasswordRequest,
  VerifyEmailRequest,
} from '~~/shared/types/Auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const initialized = ref(false)
  const error = ref<string | null>(null)
  const pendingVerificationEmail = ref<string | null>(null)

  const isAuthenticated = computed(() => !!user.value)
  const isEmailVerified = computed(() => user.value?.is_email_verified ?? false)

  const authService = useAuthService()

  const setPendingVerificationEmail = (email: string) => {
    pendingVerificationEmail.value = email.trim().toLowerCase()
  }

  const clearPendingVerificationEmail = () => {
    pendingVerificationEmail.value = null
  }

  const fetchUser = async () => {
    loading.value = true
    error.value = null
    try {
      const currentUser = await authService.getMe()
      user.value = currentUser
    } catch {
      user.value = null
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  const login = async (credentials: LoginRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.login(credentials)
      user.value = response.user
      initialized.value = true
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || err?.message || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (data: RegisterRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.register(data)
      setPendingVerificationEmail(data.email)
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || err?.message || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const verifyEmail = async (data: VerifyEmailRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.verifyEmail(data)
      if (user.value && user.value.email === data.email) {
        user.value.is_email_verified = true
      }
      clearPendingVerificationEmail()
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || err?.message || 'Email verification failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const resendVerification = async (email: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.resendVerification({ email })
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || err?.message || 'Failed to resend code'
      throw err
    } finally {
      loading.value = false
    }
  }

  const forgotPassword = async (data: ForgotPasswordRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.forgotPassword(data)
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || err?.message || 'Failed to request password reset'
      throw err
    } finally {
      loading.value = false
    }
  }

  const resetPassword = async (data: ResetPasswordRequest) => {
    loading.value = true
    error.value = null
    try {
      const response = await authService.resetPassword(data)
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || err?.message || 'Failed to reset password'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      await authService.logout()
    } catch {
      // Ignore error on logout
    } finally {
      user.value = null
      pendingVerificationEmail.value = null
      initialized.value = true
      loading.value = false
    }
  }

  return {
    user,
    loading,
    initialized,
    error,
    pendingVerificationEmail,
    setPendingVerificationEmail,
    clearPendingVerificationEmail,
    isAuthenticated,
    isEmailVerified,
    fetchUser,
    login,
    register,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    logout,
  }
})
