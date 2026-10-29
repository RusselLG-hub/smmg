<script setup lang="ts">
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  middleware: 'guest',
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Step 1: request code, Step 2: enter code & new password
const currentStep = ref<1 | 2>(route.query.step === 'reset' ? 2 : 1)
const email = ref((route.query.email as string) || '')
const code = ref('')
const form = reactive({
  password: '',
  confirmPassword: '',
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const localError = ref<string | null>(null)
const localSuccess = ref<string | null>(null)
const isSubmitting = ref(false)
const resendCooldown = ref(0)
let cooldownTimer: ReturnType<typeof setInterval> | null = null

const maskedEmail = computed(() => {
  const [name = '', domain = ''] = email.value.split('@')
  if (!domain) return email.value
  const visible = name.slice(0, Math.min(2, name.length))
  return `${visible}${'*'.repeat(Math.max(2, name.length - visible.length))}@${domain}`
})

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

onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

const startResendCooldown = () => {
  resendCooldown.value = 30
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    resendCooldown.value -= 1
    if (resendCooldown.value <= 0 && cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

const getErrorMessage = (err: any, fallback: string) => {
  const detail = err?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d.msg.replace(/^Value error,\s*/i, '')).join(', ')
  }
  return typeof detail === 'string' && detail.trim() ? detail : fallback
}

const handleRequestCode = async () => {
  localError.value = null
  localSuccess.value = null
  const normalizedEmail = email.value.trim().toLowerCase()

  if (!normalizedEmail) {
    localError.value = 'Please enter your email address'
    return
  }

  isSubmitting.value = true
  try {
    const res = await authStore.forgotPassword({ email: normalizedEmail })
    localSuccess.value = res.message || 'If an account exists with that email, a password reset code has been sent.'
    currentStep.value = 2
    startResendCooldown()
  } catch (err: any) {
    localError.value = getErrorMessage(err, 'Failed to send password reset code. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const handleResendCode = async () => {
  if (resendCooldown.value > 0 || isSubmitting.value) return
  await handleRequestCode()
}

const handleResetPassword = async () => {
  localError.value = null
  localSuccess.value = null
  const normalizedEmail = email.value.trim().toLowerCase()
  const normalizedCode = code.value.trim()

  if (!normalizedEmail || !normalizedCode) {
    localError.value = 'Please provide both your email and the 6-digit verification code.'
    return
  }

  if (!/^\d{6}$/.test(normalizedCode)) {
    localError.value = 'Verification code must be 6 digits.'
    return
  }

  if (!allRequirementsMet.value) {
    localError.value = 'Password must meet all security requirements.'
    return
  }

  if (form.password !== form.confirmPassword) {
    localError.value = 'Passwords do not match.'
    return
  }

  isSubmitting.value = true
  try {
    await authStore.resetPassword({
      email: normalizedEmail,
      code: normalizedCode,
      new_password: form.password,
    })
    await router.push('/login?reset=success')
  } catch (err: any) {
    localError.value = getErrorMessage(err, 'Failed to reset password. Please verify your code and try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <CommonAuthPageShell
    eyebrow="Account recovery"
    :title="currentStep === 1 ? 'Reset your password' : 'Create new password'"
    :description="
      currentStep === 1
        ? 'Enter the email connected to your account and we will send you a verification code.'
        : 'Enter the 6-digit code sent to your email and choose a strong new password.'
    "
    panel-title="Regain seamless access to your care."
    panel-description="Resetting your password is quick and secure so you can get back to managing your health appointments and doctor visits."
  >
    <template #icon>
      <LucideKeyRound class="h-6 w-6" />
    </template>

    <!-- Step Progress Indicator -->
    <div class="mb-6 flex items-center gap-3">
      <div class="flex items-center gap-2">
        <span
          class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors"
          :class="
            currentStep === 1
              ? 'bg-primary-600 text-white'
              : 'bg-primary-100 text-primary-700'
          "
        >
          1
        </span>
        <span class="text-xs font-semibold text-gray-700">Request code</span>
      </div>
      <div class="h-0.5 flex-1 bg-gray-200" />
      <div class="flex items-center gap-2">
        <span
          class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors"
          :class="
            currentStep === 2
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-400'
          "
        >
          2
        </span>
        <span class="text-xs font-semibold" :class="currentStep === 2 ? 'text-gray-700' : 'text-gray-400'">Set new password</span>
      </div>
    </div>

    <!-- Error Alert -->
    <div
      v-if="localError"
      class="mb-5 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
      role="alert"
    >
      <LucideAlertCircle class="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
      <span>{{ localError }}</span>
    </div>

    <!-- Success Alert -->
    <div
      v-if="localSuccess"
      class="mb-5 flex items-start gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
      role="status"
    >
      <LucideCheckCircle2 class="mt-0.5 h-5 w-5 shrink-0 text-green-600" />
      <span>{{ localSuccess }}</span>
    </div>

    <!-- Step 1: Email Form -->
    <form v-if="currentStep === 1" class="space-y-5" @submit.prevent="handleRequestCode">
      <div>
        <label for="recovery-email" class="form-label mb-1">
          Email Address
        </label>
        <input
          id="recovery-email"
          v-model="email"
          type="email"
          required
          autocomplete="email"
          placeholder="you@example.com"
          class="form-input w-full"
          :disabled="isSubmitting"
        />
      </div>

      <button
        type="submit"
        :disabled="isSubmitting || !email.trim()"
        class="btn btn-primary w-full py-3 text-base"
      >
        <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
        <span>{{ isSubmitting ? 'Sending code...' : 'Send reset code' }}</span>
      </button>
    </form>

    <!-- Step 2: Code & New Password Form -->
    <form v-else class="space-y-5" @submit.prevent="handleResetPassword">
      <div class="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-600">
        Reset code sent to <strong class="font-semibold text-gray-900">{{ maskedEmail }}</strong>.
        <button
          type="button"
          class="ml-1 text-primary-600 hover:text-primary-700 underline font-medium"
          @click="currentStep = 1"
        >
          Change email
        </button>
      </div>

      <div>
        <label for="code" class="form-label mb-1">
          6-Digit Verification Code
        </label>
        <input
          id="code"
          v-model="code"
          type="text"
          required
          inputmode="numeric"
          autocomplete="one-time-code"
          pattern="[0-9]{6}"
          maxlength="6"
          placeholder="000000"
          class="form-input w-full text-center font-mono text-lg font-bold tracking-[0.35em]"
        />
      </div>

      <div>
        <label for="new-password" class="form-label mb-1">
          New Password
        </label>
        <div class="relative">
          <input
            id="new-password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            autocomplete="new-password"
            placeholder="••••••••"
            class="form-input w-full pr-10"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            @click="showPassword = !showPassword"
          >
            <LucideEyeOff v-if="showPassword" class="h-4 w-4" />
            <LucideEye v-else class="h-4 w-4" />
          </button>
        </div>

        <!-- Password Strength Meter -->
        <div v-if="form.password.length > 0" class="mt-2.5">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-gray-500">Password strength:</span>
            <span
              class="font-medium"
              :class="{
                'text-red-600': metCount <= 2,
                'text-amber-600': metCount > 2 && metCount <= 4,
                'text-emerald-600': metCount === 5,
              }"
            >
              {{ strengthLabel }}
            </span>
          </div>
          <div class="grid grid-cols-5 gap-1 h-1.5 rounded-full overflow-hidden bg-gray-100">
            <div
              v-for="i in 5"
              :key="i"
              class="rounded-full transition-all duration-300"
              :class="i <= metCount ? strengthColor : 'bg-gray-200'"
            />
          </div>
        </div>

        <!-- Checklist -->
        <ul class="mt-2.5 grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs">
          <li
            v-for="req in passwordRequirements"
            :key="req.id"
            class="flex items-center gap-1.5 transition-colors"
            :class="req.met ? 'text-emerald-700 font-medium' : 'text-gray-400'"
          >
            <LucideCheckCircle2 v-if="req.met" class="h-3.5 w-3.5 text-emerald-500 shrink-0" />
            <LucideCircle v-else class="h-3.5 w-3.5 text-gray-300 shrink-0" />
            <span>{{ req.label }}</span>
          </li>
        </ul>
      </div>

      <div>
        <label for="confirm-password" class="form-label mb-1">
          Confirm New Password
        </label>
        <div class="relative">
          <input
            id="confirm-password"
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            required
            autocomplete="new-password"
            placeholder="••••••••"
            class="form-input w-full pr-10"
            :class="{
              '!border-red-400': form.confirmPassword.length > 0 && !passwordsMatch,
              '!border-emerald-400': passwordsMatch,
            }"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
            :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <LucideEyeOff v-if="showConfirmPassword" class="h-4 w-4" />
            <LucideEye v-else class="h-4 w-4" />
          </button>
        </div>
        <p
          v-if="form.confirmPassword.length > 0 && !passwordsMatch"
          class="mt-1 text-xs text-red-600"
        >
          Passwords do not match
        </p>
      </div>

      <button
        type="submit"
        :disabled="isSubmitting || !allRequirementsMet || !passwordsMatch || code.length < 6"
        class="btn btn-primary w-full py-3 text-base"
      >
        <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
        <span>{{ isSubmitting ? 'Resetting password...' : 'Reset password' }}</span>
      </button>

      <button
        type="button"
        :disabled="isSubmitting || resendCooldown > 0"
        class="btn btn-secondary w-full py-2.5 text-sm"
        @click="handleResendCode"
      >
        <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
        <LucideRefreshCw v-else class="h-4 w-4" />
        <span v-if="resendCooldown > 0">Resend code in {{ resendCooldown }}s</span>
        <span v-else>Resend verification code</span>
      </button>
    </form>

    <template #footer>
      <p>
        Remember your password?
        <NuxtLink to="/login" class="font-medium text-primary-600 hover:text-primary-700">
          Sign in
        </NuxtLink>
      </p>
    </template>
  </CommonAuthPageShell>
</template>
