<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePatientService } from '~/services/patient'
import { useUploadService } from '~/services/upload'
import { useAuthStore } from '~/stores/auth'
import type { PatientProfile } from '~~/shared/types/Patient'
import { normalizePhilippineMobile } from '~/utils/phone'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const patientService = usePatientService()
const uploadService = useUploadService()
const profileImageUrl = useState<string | null>('patient-profile-image-url', () => null)

const profile = ref<PatientProfile | null>(null)
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)

const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

const form = reactive({
  name: '',
  date_of_birth: '',
  gender: '',
  phone: '',
  address: '',
  profile_image_url: '',
})

onMounted(async () => {
  try {
    const res = await patientService.getMyProfile()
    profile.value = res
    form.name = res.user.name
    form.date_of_birth = res.date_of_birth || ''
    form.gender = res.gender || ''
    form.phone = res.phone || ''
    form.address = res.address || ''
    form.profile_image_url = res.profile_image_url || ''
    profileImageUrl.value = res.profile_image_url || null
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to load profile'
  } finally {
    loading.value = false
  }
})

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const file = target.files[0]
  uploading.value = true
  successMsg.value = null
  errorMsg.value = null
  try {
    const res = await uploadService.uploadImage(file)
    const updated = await patientService.updateMyProfile({ profile_image_url: res.url })
    profile.value = updated
    form.profile_image_url = updated.profile_image_url || res.url
    profileImageUrl.value = form.profile_image_url
    successMsg.value = 'Profile photo uploaded and saved.'
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to upload image'
  } finally {
    uploading.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  successMsg.value = null
  errorMsg.value = null
  const normalizedPhone = form.phone ? normalizePhilippineMobile(form.phone) : null
  if (form.phone && !normalizedPhone) {
    errorMsg.value = 'Enter a valid Philippine mobile number, such as 0917 123 4567.'
    saving.value = false
    return
  }
  try {
    const updated = await patientService.updateMyProfile({
      name: form.name,
      date_of_birth: form.date_of_birth || null,
      gender: form.gender || null,
      phone: normalizedPhone,
      address: form.address || null,
      profile_image_url: form.profile_image_url || null,
    })
    profile.value = updated
    profileImageUrl.value = updated.profile_image_url || null
    if (authStore.user) {
      authStore.user.name = form.name
    }
    successMsg.value = 'Profile updated successfully'
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to update profile'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="profile-page">
    <div class="profile-panel">
      <div class="profile-heading flex items-center gap-4">
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-600 text-white shadow-lg shadow-primary-600/20">
          <LucideUserCheck class="h-6 w-6" />
        </div>
        <div class="relative">
          <p class="section-label">Patient account</p>
          <h1 class="mt-1 text-2xl font-bold tracking-tight text-slate-950">Patient Profile</h1>
          <p class="mt-1 text-sm text-slate-600">Keep your personal and contact information up to date.</p>
        </div>
      </div>

      <div class="profile-body">

      <div v-if="loading" class="flex justify-center py-12">
        <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
      </div>

      <template v-else>
        <!-- Alerts -->
        <div v-if="successMsg" class="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <LucideCheckCircle2 class="h-5 w-5 text-green-500 shrink-0" />
          <span>{{ successMsg }}</span>
        </div>

        <div v-if="errorMsg" class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <LucideAlertCircle class="h-5 w-5 text-red-500 shrink-0" />
          <span>{{ errorMsg }}</span>
        </div>

        <form class="space-y-6" @submit.prevent="handleSave">
          <!-- Profile Picture Section -->
          <div class="flex items-center gap-6">
            <div class="relative h-20 w-20 rounded-full overflow-hidden bg-gray-100 border border-gray-300 flex items-center justify-center shrink-0">
              <BaseAvatar :src="form.profile_image_url" :alt="`${form.name || 'Patient'} avatar`" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Profile Photo</label>
              <div class="flex items-center gap-3">
                <label class="cursor-pointer inline-flex items-center gap-2 px-3 py-1.5 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm transition-colors">
                  <LucideUpload class="h-3.5 w-3.5" />
                  <span>{{ uploading ? 'Uploading...' : 'Upload Image' }}</span>
                  <input type="file" accept="image/*" class="hidden" :disabled="uploading" @change="handleImageUpload" />
                </label>
              </div>
              <p class="text-xs text-gray-500 mt-1">JPEG, PNG, WebP or GIF up to 5MB</p>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="form-label mb-1">Full Name</label>
              <input
                v-model="form.name"
                type="text"
                required
                class="form-input w-full text-sm"
              />
            </div>

            <div>
              <label class="form-label mb-1">Email Address</label>
              <input
                :value="profile?.user.email"
                type="email"
                disabled
                class="form-input w-full text-sm bg-gray-50 cursor-not-allowed"
              />
            </div>

            <div>
              <label class="form-label mb-1">Date of Birth</label>
              <input
                v-model="form.date_of_birth"
                type="date"
                class="form-input w-full text-sm"
              />
            </div>

            <div>
              <label class="form-label mb-1">Gender</label>
              <select
                v-model="form.gender"
                class="form-input w-full text-sm"
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
            </div>

            <div>
              <label class="form-label mb-1">Mobile Number (Philippines)</label>
              <input
                v-model="form.phone"
                type="tel"
                inputmode="tel"
                autocomplete="tel"
                placeholder="0917 123 4567"
                class="form-input w-full text-sm"
              />
              <p class="mt-1 text-xs text-gray-500">Use 09XXXXXXXXX or +639XXXXXXXXX.</p>
            </div>

            <div>
              <label class="form-label mb-1">Address</label>
              <input
                v-model="form.address"
                type="text"
                placeholder="123 Health Ave, City"
                class="form-input w-full text-sm"
              />
            </div>
          </div>

          <div class="pt-4 border-t border-gray-200 flex justify-end">
            <button
              type="submit"
              :disabled="saving"
              class="btn btn-primary"
            >
              <LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" />
              <LucideSave v-else class="h-4 w-4" />
              <span>{{ saving ? 'Saving Changes...' : 'Save Profile' }}</span>
            </button>
          </div>
        </form>
      </template>
      </div>
    </div>
    <FeaturesProfileChangePasswordCard v-if="profile" class="mt-6" :email="profile.user.email" />
  </div>
</template>
