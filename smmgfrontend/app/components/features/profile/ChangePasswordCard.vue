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

const getError = (err: any, fallback: string) => err?.data?.detail || err?.message || fallback

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
  if (form.newPassword.length < 8) {
    errorMsg.value = 'New password must be at least 8 characters.'
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
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="form-label mb-1" for="new-password">New password</label>
          <input id="new-password" v-model="form.newPassword" type="password" autocomplete="new-password" minlength="8" maxlength="128" required class="form-input w-full" />
        </div>
        <div>
          <label class="form-label mb-1" for="confirm-password">Confirm new password</label>
          <input id="confirm-password" v-model="form.confirmPassword" type="password" autocomplete="new-password" minlength="8" maxlength="128" required class="form-input w-full" />
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
