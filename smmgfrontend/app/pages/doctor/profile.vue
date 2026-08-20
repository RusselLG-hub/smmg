<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useDoctorsService } from '~/services/doctors'
import { useSpecialtiesStore } from '~/stores/specialties'
import { useUploadService } from '~/services/upload'
import { useAuthStore } from '~/stores/auth'
import type { Doctor } from '~~/shared/types/Doctor'
import { normalizePhilippineMobile } from '~/utils/phone'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const doctorsService = useDoctorsService()
const specialtiesStore = useSpecialtiesStore()
const uploadService = useUploadService()
const profileImageUrl = useState<string | null>('patient-profile-image-url', () => null)

const doctorProfile = ref<Doctor | null>(null)
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)

const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

const form = reactive({
  name: '',
  email: '',
  title: '',
  specialty_id: '',
  phone: '',
  bio: '',
  profile_image_url: '',
})

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchUser()
  }
  form.name = authStore.user?.name || ''
  form.email = authStore.user?.email || ''

  try {
    await specialtiesStore.fetchSpecialties(true)
    const res = await doctorsService.getMyProfile()
    doctorProfile.value = res
    form.name = res.user.name
    form.email = res.user.email
    form.title = res.title || ''
    form.specialty_id = res.specialty_id || ''
    form.phone = res.phone || ''
    form.bio = res.bio || ''
    form.profile_image_url = res.profile_image_url || ''
    profileImageUrl.value = res.profile_image_url || null
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to load doctor profile'
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
    const updated = await doctorsService.updateMyProfile({ profile_image_url: res.url })
    doctorProfile.value = updated
    form.profile_image_url = updated.profile_image_url || res.url
    profileImageUrl.value = form.profile_image_url
    successMsg.value = 'Profile photo uploaded and saved.'
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to upload profile photo'
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
    const updated = await doctorsService.updateMyProfile({
      name: form.name,
      email: form.email,
      title: form.title || null,
      specialty_id: form.specialty_id || null,
      phone: normalizedPhone,
      bio: form.bio || null,
      profile_image_url: form.profile_image_url || null,
    })
    doctorProfile.value = updated
    profileImageUrl.value = updated.profile_image_url || null
    if (authStore.user) {
      authStore.user.name = form.name
      authStore.user.email = form.email
    }
    successMsg.value = 'Doctor profile and avatar updated successfully'
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
        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-600 text-white shadow-lg shadow-teal-600/20">
          <LucideStethoscope class="h-6 w-6" />
        </div>
        <div class="relative">
          <p class="section-label">Professional identity</p>
          <h1 class="mt-1 text-2xl font-bold tracking-tight text-slate-950">Doctor Profile</h1>
          <p class="mt-1 text-sm text-slate-600">Manage your photo, credentials, specialty, and biography.</p>
        </div>
      </div>

      <div class="profile-body">

      <div v-if="loading" class="flex justify-center py-12">
        <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
      </div>

      <template v-else>
        <!-- Alerts -->
        <BaseAlertBanner v-if="successMsg" class="mb-6" type="success" :message="successMsg" @dismiss="successMsg = null" />
        <BaseAlertBanner v-if="errorMsg" class="mb-6" type="error" :message="errorMsg" @dismiss="errorMsg = null" />

        <form class="space-y-6" @submit.prevent="handleSave">
          <!-- Profile Photo / Avatar Upload Section -->
          <div class="rounded-2xl bg-gradient-to-br from-teal-700 via-teal-600 to-primary-700 p-6 text-white shadow-lg sm:flex sm:items-center sm:gap-6">
            <div class="relative mb-4 h-28 w-28 shrink-0 overflow-hidden rounded-full border-4 border-white/70 bg-white shadow-xl sm:mb-0">
              <BaseAvatar :src="form.profile_image_url" :alt="`${form.name || 'Doctor'} avatar`" />
            </div>

            <div>
              <p class="text-xl font-bold">Dr. {{ form.name || 'Doctor profile' }}</p>
              <p class="mb-3 text-sm text-white/80">{{ form.title || 'Medical professional' }} · {{ form.email }}</p>
              <div class="flex items-center gap-3">
                <label class="btn btn-secondary cursor-pointer">
                  <LucideUpload class="h-4 w-4" />
                  <span>{{ uploading ? 'Uploading Photo...' : 'Upload Avatar Image' }}</span>
                  <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" class="hidden" :disabled="uploading" @change="handleImageUpload" />
                </label>
              </div>
              <p class="mt-2 text-xs text-white/75">JPEG, PNG, WebP or GIF up to 5MB. Used in the directory and appointment cards.</p>
            </div>
          </div>

          <div class="space-y-4 border-t border-gray-100 pt-6">
            <h2 class="flex items-center gap-2 text-base font-bold text-gray-900"><LucideBadgeCheck class="h-5 w-5 text-teal-600" /> Professional information</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="form-label mb-1">Doctor Full Name</label>
              <input
                v-model="form.name"
                type="text"
                required
                maxlength="255"
                class="form-input w-full text-sm"
              />
            </div>

            <div>
              <label class="form-label mb-1">Email Address</label>
              <input
                v-model="form.email"
                type="email"
                required
                autocomplete="email"
                class="form-input w-full text-sm"
              />
            </div>

            <div>
              <label class="form-label mb-1">Title / Credentials</label>
              <input
                v-model="form.title"
                type="text"
                placeholder="e.g. MD, FACP, Pediatric Specialist"
                maxlength="100"
                class="form-input w-full text-sm"
              />
            </div>

            <div>
              <label class="form-label mb-1">Specialty Department</label>
              <select
                v-model="form.specialty_id"
                class="form-input w-full text-sm"
              >
                <option value="">Select Specialty</option>
                <option v-for="s in specialtiesStore.specialties" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>

            <div class="sm:col-span-2">
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
          </div>
          </div>

          <div>
            <label class="form-label mb-1">Biography & Medical Background</label>
            <textarea
              v-model="form.bio"
              rows="4"
              maxlength="1000"
              placeholder="Describe your qualifications, background, and medical care approach..."
              class="form-textarea w-full text-sm"
            ></textarea>
          </div>

          <div class="pt-4 border-t border-gray-200 flex justify-end">
            <button
              type="submit"
              :disabled="saving || uploading"
              class="btn btn-primary px-6 py-2.5 flex items-center gap-2"
            >
              <LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" />
              <LucideSave v-else class="h-4 w-4" />
              <span>{{ saving ? 'Saving Changes...' : 'Save Doctor Profile' }}</span>
            </button>
          </div>
        </form>
      </template>
      </div>
    </div>
    <FeaturesProfileChangePasswordCard v-if="authStore.user?.email" class="mt-6" :email="authStore.user.email" />
  </div>
</template>
