import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return

  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.fetchUser()
  }

  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }

  if (!authStore.isEmailVerified) {
    if (authStore.user?.email) {
      authStore.setPendingVerificationEmail(authStore.user.email)
    }
    return navigateTo('/verify-email')
  }
})
