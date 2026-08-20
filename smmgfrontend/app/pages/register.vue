<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  middleware: 'guest',
})

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const localError = ref<string | null>(null)
const isSubmitting = ref(false)

const handleRegister = async () => {
  localError.value = null

  if (!form.name || !form.email || !form.password || !form.confirmPassword) {
    localError.value = 'Please fill out all fields'
    return
  }

  if (form.password.length < 8) {
    localError.value = 'Password must be at least 8 characters long'
    return
  }

  if (form.password !== form.confirmPassword) {
    localError.value = 'Passwords do not match'
    return
  }

  isSubmitting.value = true
  try {
    await authStore.register({
      name: form.name,
      email: form.email,
      password: form.password,
    })
    await router.push('/verify-email')
  } catch (err: any) {
    localError.value = err?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <CommonAuthPageShell
    eyebrow="Get started"
    title="Create your account"
    description="Join SMMG Healthcare to find doctors and manage appointments."
    panel-title="A simpler path to your next appointment."
    panel-description="Create your account, verify your email, and start exploring available doctors, services, and schedules."
  >
    <template #icon><LucideUserPlus class="h-6 w-6" /></template>

      <!-- Error Alert -->
      <div
        v-if="localError"
        class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center gap-2"
        role="alert"
      >
        <LucideAlertCircle class="h-5 w-5 text-red-500 shrink-0" />
        <span>{{ localError }}</span>
      </div>

      <form class="space-y-4" @submit.prevent="handleRegister">
        <div>
          <label for="name" class="form-label mb-1">
            Full Name
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            autocomplete="name"
            placeholder="John Doe"
            class="form-input w-full"
          />
        </div>

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
            autocomplete="new-password"
            placeholder="At least 8 characters"
            class="form-input w-full"
          />
        </div>

        <div>
          <label for="confirmPassword" class="form-label mb-1">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            required
            autocomplete="new-password"
            placeholder="Repeat password"
            class="form-input w-full"
          />
        </div>

        <div class="pt-2">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="btn btn-primary w-full py-3 text-base"
          >
            <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
            <span>{{ isSubmitting ? 'Creating account...' : 'Create Account' }}</span>
          </button>
        </div>
      </form>

      <template #footer>
        Already have an account?
        <NuxtLink to="/login" class="font-medium text-primary-600 hover:text-primary-700">
          Sign in
        </NuxtLink>
      </template>
  </CommonAuthPageShell>
</template>
