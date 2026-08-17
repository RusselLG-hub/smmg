import { useAuthStore } from '~/stores/auth'

/**
 * Restore the cookie-backed session before every page is rendered. Public
 * pages also use the authenticated dashboard shell when a user is signed in,
 * so they must not wait until the layout's onMounted hook to discover that
 * session after a full browser refresh.
 */
export default defineNuxtRouteMiddleware(async () => {
  // The access token belongs to the API subdomain, so it is unavailable to
  // the Nuxt server during SSR. Restore the session from the browser instead.
  if (import.meta.server) return

  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.fetchUser()
  }
})
