<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useAuthService } from '~/services/auth'
import { useAuthStore } from '~/stores/auth'
import { useUploadService } from '~/services/upload'

definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const authService = useAuthService()
const uploadService = useUploadService()
const profileImageUrl = useState<string | null>('patient-profile-image-url', () => null)
const saving = ref(false)
const uploading = ref(false)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)
const form = reactive({
  name: authStore.user?.name || '',
  profile_image_url: authStore.user?.profile_image_url || '',
})

if (!authStore.user) {
  await authStore.fetchUser()
  form.name = authStore.user?.name || ''
  form.profile_image_url = authStore.user?.profile_image_url || ''
}

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  uploading.value = true
  errorMsg.value = null
  try {
    const response = await uploadService.uploadImage(file)
    form.profile_image_url = response.url
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Failed to upload avatar'
  } finally {
    uploading.value = false
    target.value = ''
  }
}

const handleSave = async () => {
  saving.value = true
  successMsg.value = null
  errorMsg.value = null
  try {
    const user = await authService.updateMe({
      name: form.name,
      profile_image_url: form.profile_image_url || null,
    })
    authStore.user = user
    profileImageUrl.value = user.profile_image_url || null
    successMsg.value = 'Profile updated successfully.'
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Failed to update profile'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-4 py-10">
    <section class="card p-6 sm:p-8">
      <div class="flex items-center gap-3 border-b border-gray-200 pb-6 mb-6">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-700">
          <LucideUserRound class="h-5 w-5" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">My Profile</h1>
          <p class="text-sm text-gray-600">Manage your account details and security.</p>
        </div>
      </div>

      <div v-if="successMsg" class="mb-5 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">{{ successMsg }}</div>
      <div v-if="errorMsg" class="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ errorMsg }}</div>

      <form class="space-y-5" @submit.prevent="handleSave">
        <div class="flex items-center gap-5 rounded-xl border border-primary-100 bg-primary-50/40 p-4">
          <div class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full border-2 border-primary-200 bg-white text-xl font-bold text-primary-700">
            <img v-if="form.profile_image_url" :src="form.profile_image_url" :alt="`${form.name || 'Staff'} avatar`" class="h-full w-full object-cover" />
            <span v-else>{{ (form.name || 'S').charAt(0).toUpperCase() }}</span>
          </div>
          <div>
            <label class="mb-2 block text-sm font-semibold text-gray-900">Profile Avatar</label>
            <label class="btn cursor-pointer border border-primary-300 bg-white px-4 py-2 text-primary-700 shadow-sm hover:bg-primary-50">
              <LucideLoader2 v-if="uploading" class="h-4 w-4 animate-spin" />
              <LucideUpload v-else class="h-4 w-4" />
              <span>{{ uploading ? 'Uploading...' : 'Upload Avatar' }}</span>
              <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" class="hidden" :disabled="uploading" @change="handleImageUpload" />
            </label>
            <p class="mt-2 text-xs text-gray-500">JPEG, PNG, WebP or GIF up to 5MB.</p>
          </div>
        </div>
        <div>
          <label class="form-label mb-1" for="account-name">Full Name</label>
          <input id="account-name" v-model.trim="form.name" type="text" autocomplete="name" required maxlength="255" class="form-input w-full" />
        </div>
        <div>
          <label class="form-label mb-1" for="account-email">Email Address</label>
          <input id="account-email" :value="authStore.user?.email" type="email" disabled class="form-input w-full bg-gray-50 cursor-not-allowed" />
          <p class="mt-1 text-xs text-gray-500">This is the email used for account verification.</p>
        </div>
        <div class="flex justify-end border-t border-gray-200 pt-4">
          <button type="submit" class="btn btn-primary" :disabled="saving || uploading">
            <LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" />
            <LucideSave v-else class="h-4 w-4" />
            <span>{{ saving ? 'Saving...' : 'Save Profile' }}</span>
          </button>
        </div>
      </form>
    </section>

    <FeaturesProfileChangePasswordCard v-if="authStore.user" class="mt-6" :email="authStore.user.email" />
  </div>
</template>
