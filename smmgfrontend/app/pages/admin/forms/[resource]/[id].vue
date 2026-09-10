<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useDoctorsService } from '~/services/doctors'
import { useDoctorsStore } from '~/stores/doctors'
import { useSpecialtiesStore } from '~/stores/specialties'
import { useClinicServicesStore } from '~/stores/clinicServices'
import { useSchedulesStore } from '~/stores/schedules'
import { useUsersService } from '~/services/users'
import { useUploadService } from '~/services/upload'
import { normalizePhilippineMobile } from '~/utils/phone'
import { WEEKDAYS } from '~~/shared/types/Schedule'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const resource = computed(() => String(route.params.resource))
const recordId = computed(() => String(route.params.id))
const isEditing = computed(() => recordId.value !== 'new')
const validResources = ['doctors', 'staff', 'specialties', 'services', 'schedules']

if (!validResources.includes(resource.value)) {
  throw createError({ statusCode: 404, statusMessage: 'Form not found' })
}
if (isEditing.value && ['doctors', 'staff'].includes(resource.value)) {
  throw createError({ statusCode: 404, statusMessage: 'Form not found' })
}

const authStore = useAuthStore()
const doctorsService = useDoctorsService()
const doctorsStore = useDoctorsStore()
const specialtiesStore = useSpecialtiesStore()
const servicesStore = useClinicServicesStore()
const schedulesStore = useSchedulesStore()
const usersService = useUsersService()
const uploadService = useUploadService()

const isDoctor = computed(() => authStore.user?.role === 'doctor')

const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const errorMsg = ref<string | null>(null)
const successMsg = ref<string | null>(null)

const form = reactive({
  name: '', email: '', password: '', title: '', specialty_id: '', phone: '', bio: '',
  description: '', image_url: '', is_active: true, doctor_profile_id: '', day_of_week: 0,
  start_time: '08:00', end_time: '17:00',
})

const copy = computed(() => {
  const labels: Record<string, [string, string]> = {
    doctors: ['Add Doctor Account', 'Create login credentials and a professional clinic profile.'],
    staff: ['Add Staff Account', 'Create an account for a clinic staff member.'],
    specialties: [isEditing.value ? 'Edit Medical Specialty' : 'Add Medical Specialty', 'Maintain the specialty name, description, and visibility.'],
    services: [isEditing.value ? 'Edit Clinic Service' : 'Add Clinic Service', 'Maintain the service details, specialty, image, and visibility.'],
    schedules: [
      isEditing.value
        ? (isDoctor.value ? 'Edit My Schedule' : 'Edit Doctor Schedule')
        : (isDoctor.value ? 'Add Working Hours' : 'Add Doctor Schedule'),
      isDoctor.value
        ? 'Configure your weekly working hours and clinic availability.'
        : 'Configure recurring doctor availability. Appointments use the standard clinic interval.',
    ],
  }
  return labels[resource.value]
})

const backTo = computed(() => resource.value === 'schedules' ? '/admin/schedules' : `/admin?tab=${resource.value}`)

onMounted(async () => {
  try {
    if (!authStore.user) {
      await authStore.fetchUser()
    }
    if (authStore.user?.role === 'patient') {
      await navigateTo('/patient/dashboard')
      return
    }
    if (isDoctor.value && resource.value !== 'schedules') {
      await navigateTo('/doctor/dashboard')
      return
    }

    if (['doctors', 'services'].includes(resource.value)) {
      await specialtiesStore.fetchSpecialties(false)
    }
    if (resource.value === 'schedules') {
      if (isDoctor.value) {
        const myProfile = await doctorsService.getMyProfile()
        form.doctor_profile_id = myProfile.id
        if (isEditing.value) {
          await schedulesStore.fetchDoctorSchedules(myProfile.id)
          const schedule = schedulesStore.schedules.find(item => item.id === recordId.value)
          if (!schedule || schedule.doctor_profile_id !== myProfile.id) {
            throw new Error('Schedule not found or unauthorized')
          }
          Object.assign(form, schedule)
        }
      } else {
        await doctorsStore.fetchDoctors(false)
        form.doctor_profile_id = String(route.query.doctor || '')
        if (isEditing.value) {
          await schedulesStore.fetchAllDoctorSchedules(doctorsStore.doctors.map(doctor => doctor.id))
          const schedule = schedulesStore.schedules.find(item => item.id === recordId.value)
          if (!schedule) throw new Error('Schedule not found')
          Object.assign(form, schedule)
        }
      }
    } else if (resource.value === 'specialties' && isEditing.value) {
      await specialtiesStore.fetchSpecialties(false)
      const specialty = specialtiesStore.specialties.find(item => item.id === recordId.value)
      if (!specialty) throw new Error('Specialty not found')
      Object.assign(form, { name: specialty.name, description: specialty.description || '', is_active: specialty.is_active })
    } else if (resource.value === 'services' && isEditing.value) {
      await servicesStore.fetchServices(false)
      const service = servicesStore.services.find(item => item.id === recordId.value)
      if (!service) throw new Error('Service not found')
      Object.assign(form, {
        name: service.name, description: service.description || '', specialty_id: service.specialty_id || '',
        image_url: service.image_url || '', is_active: service.is_active,
      })
    }
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Failed to load form data'
  } finally {
    loading.value = false
  }
})

const uploadImage = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  uploading.value = true
  errorMsg.value = null
  try {
    const result = await uploadService.uploadImage(file)
    form.image_url = result.url
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Image upload failed'
  } finally {
    uploading.value = false
    target.value = ''
  }
}

const handleSubmit = async () => {
  saving.value = true
  errorMsg.value = null
  successMsg.value = null
  try {
    if (resource.value === 'doctors') {
      const phone = form.phone ? normalizePhilippineMobile(form.phone) : null
      if (form.phone && !phone) throw new Error('Enter a valid Philippine mobile number, such as 0917 123 4567.')
      await doctorsStore.createDoctor({
        email: form.email, name: form.name, password: form.password, title: form.title || null,
        specialty_id: form.specialty_id || null, phone, bio: form.bio || null, is_active: form.is_active,
      })
    } else if (resource.value === 'staff') {
      await usersService.createStaffUser({ email: form.email, name: form.name, password: form.password })
    } else if (resource.value === 'specialties') {
      const data = { name: form.name, description: form.description || null, is_active: form.is_active }
      if (isEditing.value) await specialtiesStore.updateSpecialty(recordId.value, data)
      else await specialtiesStore.createSpecialty(data)
    } else if (resource.value === 'services') {
      const data = {
        name: form.name, description: form.description || null, specialty_id: form.specialty_id || null,
        image_url: form.image_url || null, is_active: form.is_active,
      }
      if (isEditing.value) await servicesStore.updateService(recordId.value, data)
      else await servicesStore.createService(data)
    } else {
      const data = {
        day_of_week: Number(form.day_of_week), start_time: form.start_time, end_time: form.end_time,
        is_active: form.is_active,
      }
      if (isEditing.value) await schedulesStore.updateSchedule(recordId.value, data)
      else await schedulesStore.createSchedule({ doctor_profile_id: form.doctor_profile_id, ...data })
    }
    successMsg.value = `${copy.value[0].replace(/^(Add|Edit) /, '')} saved successfully.`
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Unable to save changes'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
    <NuxtLink :to="backTo" class="mb-5 inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-900">
      <LucideArrowLeft class="h-4 w-4" /> {{ resource === 'schedules' ? (isDoctor ? 'Back to my schedule' : 'Back to doctor schedule') : 'Back to management' }}
    </NuxtLink>

    <section class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <header class="border-b border-gray-200 bg-gradient-to-r from-primary-50 via-white to-teal-50 px-6 py-6 sm:px-8">
        <p class="section-label">{{ resource === 'schedules' ? (isDoctor ? 'My schedule' : 'Doctor schedule') : 'Admin management' }}</p>
        <h1 class="mt-1 text-2xl font-bold tracking-tight text-slate-950">{{ copy[0] }}</h1>
        <p class="mt-2 text-sm text-slate-600">{{ copy[1] }}</p>
      </header>

      <div v-if="loading" class="flex justify-center py-20"><LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" /></div>
      <form v-else class="space-y-6 p-6 sm:p-8" @submit.prevent="handleSubmit">
        <BaseAlertBanner v-if="successMsg" type="success" :message="successMsg" @dismiss="successMsg = null" />
        <BaseAlertBanner v-if="errorMsg" type="error" :message="errorMsg" @dismiss="errorMsg = null" />

        <div v-if="resource === 'doctors' || resource === 'staff'" class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div><label class="form-label">Full Name</label><input v-model.trim="form.name" required maxlength="255" class="form-input" /></div>
          <div><label class="form-label">Email Address</label><input v-model.trim="form.email" type="email" required class="form-input" /></div>
          <div class="sm:col-span-2"><label class="form-label">Temporary Password</label><input v-model="form.password" type="password" required minlength="8" maxlength="128" class="form-input" /></div>
          <template v-if="resource === 'doctors'">
            <div><label class="form-label">Title / Credentials</label><input v-model="form.title" maxlength="100" class="form-input" placeholder="MD, FACP" /></div>
            <div><label class="form-label">Specialty</label><select v-model="form.specialty_id" class="form-input"><option value="">Unassigned</option><option v-for="item in specialtiesStore.specialties" :key="item.id" :value="item.id">{{ item.name }}</option></select></div>
            <div class="sm:col-span-2"><label class="form-label">Mobile Number</label><input v-model="form.phone" class="form-input" placeholder="0917 123 4567" /></div>
            <div class="sm:col-span-2"><label class="form-label">Biography</label><textarea v-model="form.bio" rows="4" maxlength="1000" class="form-input" /></div>
          </template>
        </div>

        <div v-else-if="resource === 'specialties'" class="space-y-5">
          <div><label class="form-label">Specialty Name</label><input v-model.trim="form.name" required maxlength="100" class="form-input" /></div>
          <div><label class="form-label">Description</label><textarea v-model="form.description" rows="5" maxlength="500" class="form-input" /></div>
        </div>

        <div v-else-if="resource === 'services'" class="space-y-5">
          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div><label class="form-label">Service Name</label><input v-model.trim="form.name" required maxlength="150" class="form-input" /></div>
            <div><label class="form-label">Associated Specialty</label><select v-model="form.specialty_id" class="form-input"><option value="">No specialty</option><option v-for="item in specialtiesStore.specialties" :key="item.id" :value="item.id">{{ item.name }}</option></select></div>
          </div>
          <div><label class="form-label">Description</label><textarea v-model="form.description" rows="5" maxlength="1000" class="form-input" /></div>
          <div>
            <label class="form-label">Service Image</label>
            <div class="mt-1 grid gap-4 rounded-xl border border-gray-200 bg-gray-50 p-4 sm:grid-cols-[12rem_1fr] sm:items-center">
              <img :src="form.image_url || '/images/default-service.svg'" class="aspect-video w-full rounded-lg border border-gray-200 bg-white object-cover" alt="Service preview" />
              <div class="space-y-3"><p class="text-sm text-gray-600">JPEG, PNG, WebP or GIF up to 5MB.</p><label class="btn btn-secondary cursor-pointer"><LucideUpload class="h-4 w-4" />{{ uploading ? 'Uploading...' : 'Choose Image' }}<input type="file" accept="image/jpeg,image/png,image/webp,image/gif" class="hidden" :disabled="uploading" @change="uploadImage" /></label><button v-if="form.image_url" type="button" class="ml-2 text-sm font-semibold text-red-600" @click="form.image_url = ''">Remove</button></div>
            </div>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div v-if="!isEditing && !isDoctor" class="sm:col-span-2">
            <label class="form-label">Doctor</label>
            <select v-model="form.doctor_profile_id" required class="form-input">
              <option value="" disabled>Select a doctor</option>
              <option v-for="doctor in doctorsStore.doctors" :key="doctor.id" :value="doctor.id">
                Dr. {{ doctor.user.name }}
              </option>
            </select>
          </div>
          <div><label class="form-label">Weekday</label><select v-model="form.day_of_week" class="form-input"><option v-for="(day, index) in WEEKDAYS" :key="day" :value="index">{{ day }}</option></select></div>
          <div><label class="form-label">Start Time</label><input v-model="form.start_time" type="time" required class="form-input" /></div>
          <div><label class="form-label">End Time</label><input v-model="form.end_time" type="time" required class="form-input" /></div>
        </div>

        <label v-if="resource !== 'staff'" class="flex items-center gap-3 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-800">
          <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded text-primary-600" /> Active and visible
        </label>

        <div class="flex flex-col-reverse gap-3 border-t border-gray-200 pt-6 sm:flex-row sm:justify-end">
          <NuxtLink :to="backTo" class="btn btn-secondary justify-center">Cancel</NuxtLink>
          <button type="submit" class="btn btn-primary justify-center" :disabled="saving || uploading"><LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" /><LucideSave v-else class="h-4 w-4" />{{ saving ? 'Saving...' : 'Save Changes' }}</button>
        </div>
      </form>
    </section>
  </div>
</template>
