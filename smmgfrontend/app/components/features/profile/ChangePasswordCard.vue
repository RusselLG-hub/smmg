<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useAuthService } from '~/services/auth'

const props = defineProps<{
  email: string
}>()

const authService = useAuthService()
const step = ref<1 | 2>(1)
const sending = ref(false)
const submitting = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)
const form = reactive({
  code: '',
  newPassword: '',
  confirmPassword: '',
})

const maskedEmail = computed(() => {
  const [local, domain] = props.email.split('@')
  if (!local || !domain) return props.email
  return `${local.slice(0, 2)}${'*'.repeat(Math.max(2, local.length - 2))}@${domain}`
})

const passwordRequirements = computed(() => [
  { id: 'minChar', label: 'At least 8 characters', met: form.newPassword.length >= 8 },
  { id: 'upper', label: '1 uppercase letter (A-Z)', met: /[A-Z]/.test(form.newPassword) },
  { id: 'lower', label: '1 lowercase letter (a-z)', met: /[a-z]/.test(form.newPassword) },
  { id: 'number', label: '1 number (0-9)', met: /\d/.test(form.newPassword) },
  { id: 'special', label: '1 special character (!@#$%^&*)', met: /[^A-Za-z0-9]/.test(form.newPassword) },
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
  form.confirmPassword.length > 0 && form.newPassword === form.confirmPassword
)

const getError = (err: any, fallback: string) => {
  if (Array.isArray(err?.data?.detail)) {
    return err.data.detail.map((d: any) => d.msg.replace(/^Value error,\s*/i, '')).join(', ')
  }
  return err?.data?.detail || err?.message || fallback
}

const sendCode = async () => {
  sending.value = true
  errorMsg.value = null
  successMsg.value = null
  try {
    const response = await authService.requestPasswordChange()
    step.value = 2
    successMsg.value = response.message
  } catch (err: any) {
    errorMsg.value = getError(err, 'Failed to send verification code')
  } finally {
    sending.value = false
  }
}

const submitPassword = async () => {
  errorMsg.value = null
  successMsg.value = null
  if (!/^\d{6}$/.test(form.code)) {
    errorMsg.value = 'Enter the 6-digit verification code.'
    return
  }
  if (!allRequirementsMet.value) {
    errorMsg.value = 'New password must meet all security requirements.'
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    errorMsg.value = 'New passwords do not match.'
    return
  }

  submitting.value = true
  try {
    const response = await authService.confirmPasswordChange({
      code: form.code,
      new_password: form.newPassword,
    })
    successMsg.value = response.message
    form.code = ''
    form.newPassword = ''
    form.confirmPassword = ''
    step.value = 1
  } catch (err: any) {
    errorMsg.value = getError(err, 'Failed to change password')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="card p-6 sm:p-8" aria-labelledby="change-password-title">
    <div class="flex items-center gap-3 pb-5 border-b border-gray-200 mb-5">
      <div class="h-10 w-10 rounded-lg bg-primary-100 text-primary-700 flex items-center justify-center">
        <LucideShieldCheck class="h-5 w-5" />
      </div>
      <div>
        <h2 id="change-password-title" class="text-lg font-bold text-gray-900">Change Password</h2>
        <p class="text-sm text-gray-600">Verify the change using a code sent to your account email.</p>
      </div>
    </div>

    <div v-if="successMsg" class="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">{{ successMsg }}</div>
    <div v-if="errorMsg" class="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ errorMsg }}</div>

    <div v-if="step === 1" class="space-y-4">
      <p class="text-sm text-gray-600">Step 1 of 2: send a verification code to <strong class="text-gray-900">{{ maskedEmail }}</strong>.</p>
      <button type="button" class="btn btn-primary" :disabled="sending" @click="sendCode">
        <LucideLoader2 v-if="sending" class="h-4 w-4 animate-spin" />
        <LucideMail v-else class="h-4 w-4" />
        <span>{{ sending ? 'Sending Code...' : 'Send Verification Code' }}</span>
      </button>
    </div>

    <form v-else class="space-y-4" @submit.prevent="submitPassword">
      <p class="text-sm text-gray-600">Step 2 of 2: enter the emailed code and choose your new password.</p>
      <div>
        <label class="form-label mb-1" for="password-code">6-digit verification code</label>
        <input id="password-code" v-model.trim="form.code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" required class="form-input w-full sm:max-w-xs" placeholder="123456" />
      </div>
      <div class="space-y-4">
        <div>
          <label class="form-label mb-1" for="new-password">New password</label>
          <div class="relative">
            <input
              id="new-password"
              v-model="form.newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              autocomplete="new-password"
              maxlength="128"
              required
              class="form-input w-full pr-10"
              placeholder="Create a strong password"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
              aria-label="Toggle password visibility"
              @click="showNewPassword = !showNewPassword"
            >
              <LucideEyeOff v-if="showNewPassword" class="h-4 w-4" />
              <LucideEye v-else class="h-4 w-4" />
            </button>
          </div>

          <!-- Password Strength Bar -->
          <div v-if="form.newPassword" class="mt-2 space-y-1">
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
          <label class="form-label mb-1" for="confirm-password">Confirm new password</label>
          <div class="relative">
            <input
              id="confirm-password"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              autocomplete="new-password"
              maxlength="128"
              required
              class="form-input w-full pr-10"
              placeholder="Repeat your new password"
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
      </div>
      <div class="flex flex-wrap gap-3">
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <LucideLoader2 v-if="submitting" class="h-4 w-4 animate-spin" />
          <LucideKeyRound v-else class="h-4 w-4" />
          <span>{{ submitting ? 'Changing Password...' : 'Submit New Password' }}</span>
        </button>
        <button type="button" class="btn border border-gray-300 bg-white text-gray-700 hover:bg-gray-50" :disabled="sending || submitting" @click="sendCode">Resend Code</button>
      </div>
    </form>
  </section>
</template>
