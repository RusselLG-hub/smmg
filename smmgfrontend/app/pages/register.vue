<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
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

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const localError = ref<string | null>(null)
const isSubmitting = ref(false)

const passwordRequirements = computed(() => [
  { id: 'minChar', label: 'At least 8 characters', met: form.password.length >= 8 },
  { id: 'upper', label: '1 uppercase letter (A-Z)', met: /[A-Z]/.test(form.password) },
  { id: 'lower', label: '1 lowercase letter (a-z)', met: /[a-z]/.test(form.password) },
  { id: 'number', label: '1 number (0-9)', met: /\d/.test(form.password) },
  { id: 'special', label: '1 special character (!@#$%^&*)', met: /[^A-Za-z0-9]/.test(form.password) },
])

const metCount = computed(() => passwordRequirements.value.filter((r) => r.met).length)
const allRequirementsMet = computed(() => metCount.value === passwordRequirements.value.length)

const strengthLabel = computed(() => {
  if (metCount.value === 0) return ''
  if (metCount.value <= 2) return 'Weak'
  if (metCount.value <= 4) return 'Moderate'
  return 'Strong'
})

const strengthColor = computed(() => {
  if (metCount.value <= 2) return 'bg-red-500'
  if (metCount.value <= 4) return 'bg-amber-500'
  return 'bg-emerald-500'
})

const passwordsMatch = computed(() =>
  form.confirmPassword.length > 0 && form.password === form.confirmPassword
)

const handleRegister = async () => {
  localError.value = null

  if (!form.name || !form.email || !form.password || !form.confirmPassword) {
    localError.value = 'Please fill out all fields'
    return
  }

  const trimmedName = form.name.trim()
  const nameParts = trimmedName.split(/\s+/)
  if (nameParts.length < 2 || nameParts.some((p) => p.length < 2) || !/^[A-Za-zÀ-ÿ\s'.-]+$/.test(trimmedName)) {
    localError.value = 'Please enter your full name (at least first and last name, letters only).'
    return
  }

  if (!allRequirementsMet.value) {
    localError.value = 'Password must meet all security requirements.'
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
    if (Array.isArray(err?.data?.detail)) {
      localError.value = err.data.detail.map((d: any) => d.msg.replace(/^Value error,\s*/i, '')).join(', ')
    } else {
      localError.value = err?.data?.detail || 'Registration failed. Please try again.'
    }
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
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Create a strong password"
              class="form-input w-full pr-10"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
              aria-label="Toggle password visibility"
              @click="showPassword = !showPassword"
            >
              <LucideEyeOff v-if="showPassword" class="h-4 w-4" />
              <LucideEye v-else class="h-4 w-4" />
            </button>
          </div>

          <!-- Password Strength Bar (Visible once user starts typing) -->
          <div v-if="form.password" class="mt-2 space-y-1">
            <div class="flex items-center justify-between text-xs">
              <span class="text-gray-500 font-medium">Strength:</span>
              <span
                class="font-semibold"
                :class="{
                  'text-red-600': metCount <= 2,
                  'text-amber-600': metCount > 2 && metCount < 5,
                  'text-emerald-600': metCount === 5,
                }"
              >
                {{ strengthLabel }}
              </span>
            </div>
            <div class="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden flex gap-1">
              <div
                v-for="i in 5"
                :key="i"
                class="h-full flex-1 rounded-full transition-all duration-300"
                :class="i <= metCount ? strengthColor : 'bg-gray-200'"
              ></div>
            </div>
          </div>

          <!-- Password Requirements Checklist Display -->
          <div class="mt-2.5 p-3.5 bg-gray-50 rounded-xl border border-gray-200 text-xs">
            <p class="font-semibold text-gray-700 mb-2 flex items-center justify-between">
              <span>Password must contain:</span>
              <span v-if="allRequirementsMet" class="text-emerald-600 font-bold flex items-center gap-1">
                <LucideCheckCircle2 class="h-3.5 w-3.5" /> All criteria met
              </span>
            </p>
            <ul class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
              <li
                v-for="req in passwordRequirements"
                :key="req.id"
                class="flex items-center gap-1.5 transition-colors duration-200"
                :class="req.met ? 'text-emerald-700 font-medium' : 'text-gray-500'"
              >
                <LucideCheckCircle2
                  v-if="req.met"
                  class="h-4 w-4 text-emerald-600 shrink-0"
                />
                <span
                  v-else
                  class="h-4 w-4 flex items-center justify-center shrink-0 text-gray-300 font-bold text-xs"
                >
                  ○
                </span>
                <span>{{ req.label }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div>
          <label for="confirmPassword" class="form-label mb-1">
            Confirm Password
          </label>
          <div class="relative">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Repeat your password"
              class="form-input w-full pr-10"
              :class="{
                'border-emerald-500 focus:border-emerald-500 focus:ring-emerald-500': passwordsMatch,
                'border-red-500 focus:border-red-500 focus:ring-red-500': form.confirmPassword && !passwordsMatch
              }"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
              aria-label="Toggle confirm password visibility"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <LucideEyeOff v-if="showConfirmPassword" class="h-4 w-4" />
              <LucideEye v-else class="h-4 w-4" />
            </button>
          </div>

          <!-- Password Match Feedback -->
          <div v-if="form.confirmPassword" class="mt-1.5 text-xs flex items-center gap-1.5">
            <template v-if="passwordsMatch">
              <LucideCheckCircle2 class="h-3.5 w-3.5 text-emerald-600 shrink-0" />
              <span class="text-emerald-700 font-medium">Passwords match</span>
            </template>
            <template v-else>
              <LucideAlertCircle class="h-3.5 w-3.5 text-red-500 shrink-0" />
              <span class="text-red-600">Passwords do not match</span>
            </template>
          </div>
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
