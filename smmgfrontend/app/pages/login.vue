<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  middleware: 'guest',
})

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({
  email: '',
  password: '',
})

const localError = ref<string | null>(null)
const isSubmitting = ref(false)
const verificationSuccess = computed(() => route.query.verified === 'true')

const isUnverifiedEmailError = (detail: string) =>
  detail.toLowerCase().includes('email not verified')

const handleLogin = async () => {
  localError.value = null
  if (!form.email || !form.password) {
    localError.value = 'Please enter both email and password'
    return
  }

  isSubmitting.value = true
  try {
    const res = await authStore.login({
      email: form.email,
      password: form.password,
    })
    const roleRoutes: Record<string, string> = {
      patient: '/patient/dashboard',
      doctor: '/doctor/dashboard',
      staff: '/staff/dashboard',
      admin: '/admin/dashboard',
    }
    const target = roleRoutes[res.user?.role || authStore.user?.role || ''] || '/patient/dashboard'
    await router.push(target)
  } catch (err: any) {
    const detail = String(err?.data?.detail || 'Invalid email or password')
    if (isUnverifiedEmailError(detail)) {
      authStore.setPendingVerificationEmail(form.email)
      await router.push('/verify-email?reason=login')
      return
    }
    localError.value = detail
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <CommonAuthPageShell
    eyebrow="Welcome back"
    title="Sign in to your account"
    description="Access your appointments, profile, and healthcare tools."
    panel-title="Your healthcare plans, all in one place."
    panel-description="Return to manage appointments, review schedules, and access the tools that help you prepare for your next clinic visit."
  >
    <template #icon><LucideLogIn class="h-6 w-6" /></template>

      <div
        v-if="verificationSuccess"
        class="flex items-start gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
        role="status"
      >
        <LucideCheckCircle2 class="mt-0.5 h-5 w-5 shrink-0 text-green-600" />
        <span>Email verified successfully. You can now sign in.</span>
      </div>

      <!-- Error Alert -->
      <div
        v-if="localError"
        class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-start gap-2"
        role="alert"
      >
        <LucideAlertCircle class="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
        <p>{{ localError }}</p>
      </div>

      <form class="space-y-5" @submit.prevent="handleLogin">
        <div>
          <label for="email" class="form-label mb-1">
            Email Address
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            autocomplete="email"
            placeholder="you@example.com"
            class="form-input w-full"
          />
        </div>

        <div>
          <label for="password" class="form-label mb-1">
            Password
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
            class="form-input w-full"
          />
        </div>

        <div>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="btn btn-primary w-full py-3 text-base"
          >
            <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
            <span>{{ isSubmitting ? 'Signing in...' : 'Sign In' }}</span>
          </button>
        </div>
      </form>

      <template #footer>
        <p>
          New to SMMG?
          <NuxtLink to="/register" class="font-medium text-primary-600 hover:text-primary-700">
            Create an account
          </NuxtLink>
        </p>
      </template>
  </CommonAuthPageShell>
</template>
