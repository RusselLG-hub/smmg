import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async () => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.fetchUser()
  }

  if (authStore.isAuthenticated && authStore.user) {
    const roleRoutes: Record<string, string> = {
      patient: '/patient/dashboard',
      doctor: '/doctor/dashboard',
      staff: '/staff/dashboard',
      admin: '/admin/dashboard',
    }
    const target = roleRoutes[authStore.user.role] || '/patient/dashboard'
    return navigateTo(target)
  }
})
