<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ middleware: 'guest' })

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const code = ref('')
const localError = ref<string | null>(null)
const localSuccess = ref<string | null>(null)
const isSubmitting = ref(false)
const isResending = ref(false)
const resendCooldown = ref(0)
let cooldownTimer: ReturnType<typeof setInterval> | null = null

const hasKnownEmail = computed(() => Boolean(authStore.pendingVerificationEmail))
const cameFromLogin = computed(() => route.query.reason === 'login')
const maskedEmail = computed(() => {
  const [name = '', domain = ''] = email.value.split('@')
  if (!domain) return email.value
  const visible = name.slice(0, Math.min(2, name.length))
  return `${visible}${'*'.repeat(Math.max(2, name.length - visible.length))}@${domain}`
})

onMounted(() => {
  email.value = authStore.pendingVerificationEmail || ''
})

onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

const getErrorMessage = (err: any, fallback: string) => {
  const detail = err?.data?.detail
  return typeof detail === 'string' && detail.trim() ? detail : fallback
}

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

const handleVerify = async () => {
  localError.value = null
  localSuccess.value = null
  const normalizedEmail = email.value.trim().toLowerCase()
  const normalizedCode = code.value.trim()

  if (!normalizedEmail || !normalizedCode) {
    localError.value = 'Enter your email address and verification code.'
    return
  }
  if (!/^\d{6}$/.test(normalizedCode)) {
    localError.value = 'Enter the 6-digit code from your verification email.'
    return
  }

  isSubmitting.value = true
  try {
    await authStore.verifyEmail({ email: normalizedEmail, code: normalizedCode })
    await router.push('/login?verified=true')
  } catch (err: any) {
    localError.value = getErrorMessage(err, 'We could not verify that code. Check it and try again.')
  } finally {
    isSubmitting.value = false
  }
}

const handleResend = async () => {
  localError.value = null
  localSuccess.value = null
  const normalizedEmail = email.value.trim().toLowerCase()

  if (!normalizedEmail) {
    localError.value = 'Enter the email address you used to register.'
    return
  }

  isResending.value = true
  try {
    const response = await authStore.resendVerification(normalizedEmail)
    authStore.setPendingVerificationEmail(normalizedEmail)
    localSuccess.value = response.message || 'A new verification code has been sent. Please check your inbox.'
    startResendCooldown()
  } catch (err: any) {
    localError.value = getErrorMessage(err, 'We could not resend the code. Please try again later.')
  } finally {
    isResending.value = false
  }
}
</script>

<template>
  <CommonAuthPageShell
    eyebrow="One last step"
    title="Check your email"
    description="Verify your email address to finish setting up your SMMG account."
    panel-title="Secure your account before your first visit."
    panel-description="Email verification helps confirm your account details before you begin managing healthcare appointments."
  >
    <template #icon><LucideMailCheck class="h-6 w-6" /></template>

      <div class="mb-6 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3.5">
        <p v-if="email" class="text-sm leading-6 text-gray-600">
          We sent a 6-digit verification code to
          <strong class="font-semibold text-gray-900">{{ maskedEmail }}</strong>.
        </p>
        <p v-else class="text-sm leading-6 text-gray-600">
          Enter the email address you registered with and the 6-digit code from your message.
        </p>
      </div>

      <div v-if="cameFromLogin" class="flex items-start gap-2 rounded-lg border border-primary-200 bg-primary-50 px-4 py-3 text-sm text-primary-800" role="status">
        <LucideInfo class="mt-0.5 h-5 w-5 shrink-0" />
        <span>Please verify your email before signing in.</span>
      </div>

      <div v-if="localError" class="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
        <LucideAlertCircle class="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
        <span>{{ localError }}</span>
      </div>

      <div v-if="localSuccess" class="flex items-start gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700" role="status">
        <LucideCheckCircle2 class="mt-0.5 h-5 w-5 shrink-0 text-green-600" />
        <span>{{ localSuccess }}</span>
      </div>

      <form class="space-y-5" @submit.prevent="handleVerify">
        <div v-if="!hasKnownEmail">
          <label for="email" class="form-label">Email address</label>
          <input id="email" v-model.trim="email" type="email" required autocomplete="email" placeholder="you@example.com" class="form-input" />
        </div>

        <div>
          <label for="code" class="form-label">Verification code</label>
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
            class="form-input text-center font-mono text-lg font-bold tracking-[0.35em]"
          />
        </div>

        <button type="submit" :disabled="isSubmitting" class="btn btn-primary w-full py-2.5">
          <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
          <span>{{ isSubmitting ? 'Verifying…' : 'Verify email' }}</span>
        </button>

        <button type="button" :disabled="isResending || resendCooldown > 0" class="btn btn-secondary w-full py-2.5" @click="handleResend">
          <LucideLoader2 v-if="isResending" class="h-4 w-4 animate-spin" />
          <LucideRefreshCw v-else class="h-4 w-4" />
          <span v-if="isResending">Sending…</span>
          <span v-else-if="resendCooldown > 0">Resend available in {{ resendCooldown }}s</span>
          <span v-else>Resend code</span>
        </button>
      </form>

      <template #footer>
        <div class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
        <NuxtLink to="/login" class="font-medium text-primary-700 hover:text-primary-800">Back to sign in</NuxtLink>
        <NuxtLink to="/register" class="font-medium text-gray-600 hover:text-gray-900">Create a different account</NuxtLink>
        </div>
      </template>
  </CommonAuthPageShell>
</template>
