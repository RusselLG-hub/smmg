<script setup lang="ts">
import { computed, ref, reactive, onMounted } from 'vue'
import { useDoctorsStore } from '~/stores/doctors'
import { useSpecialtiesStore } from '~/stores/specialties'
import { useClinicServicesStore } from '~/stores/clinicServices'
import { useUploadService } from '~/services/upload'
import { useUsersService } from '~/services/users'
import { normalizePhilippineMobile } from '~/utils/phone'
import type { Doctor } from '~~/shared/types/Doctor'
import type { Specialty } from '~~/shared/types/Specialty'
import type { ClinicService } from '~~/shared/types/ClinicService'
import type { User } from '~~/shared/types/User'

definePageMeta({
  middleware: 'auth',
})

const doctorsStore = useDoctorsStore()
const specialtiesStore = useSpecialtiesStore()
const clinicServicesStore = useClinicServicesStore()
const uploadService = useUploadService()
const usersService = useUsersService()

const route = useRoute()
const requestedTab = String(route.query.tab || '')
const activeTab = ref<'doctors' | 'staff' | 'specialties' | 'services'>(
  ['doctors', 'staff', 'specialties', 'services'].includes(requestedTab)
    ? requestedTab as 'doctors' | 'staff' | 'specialties' | 'services'
    : 'doctors',
)
const staffUsers = ref<User[]>([])
const loadingStaff = ref(false)

const showDoctorModal = ref(false)
const showStaffModal = ref(false)
const showSpecialtyModal = ref(false)
const showServiceModal = ref(false)
const editingSpecialtyId = ref<string | null>(null)
const editingServiceId = ref<string | null>(null)

const actionError = ref<string | null>(null)
const actionSuccess = ref<string | null>(null)
const uploadingImage = ref(false)
type DeleteTarget = { type: 'doctor' | 'specialty' | 'service'; id: string }
const pendingDelete = ref<DeleteTarget | null>(null)
const deletingRecord = ref(false)

const deleteModalCopy = computed(() => {
  const labels = {
    doctor: ['Delete doctor account?', 'The doctor account and associated profile will be permanently removed.', 'Delete Doctor'],
    specialty: ['Delete specialty?', 'This specialty will be permanently removed from the clinic catalog.', 'Delete Specialty'],
    service: ['Delete clinic service?', 'This service will be permanently removed from the public catalog.', 'Delete Service'],
  } as const
  return labels[pendingDelete.value?.type || 'service']
})

// Forms
const doctorForm = reactive({
  email: '',
  name: '',
  password: '',
  title: '',
  specialty_id: '',
  phone: '',
  bio: '',
  profile_image_url: '',
  is_active: true,
})

const staffForm = reactive({
  email: '',
  name: '',
  password: '',
})

const specialtyForm = reactive({
  name: '',
  description: '',
  is_active: true,
})

const serviceForm = reactive({
  name: '',
  description: '',
  specialty_id: '',
  image_url: '',
  is_active: true,
})

onMounted(async () => {
  await Promise.all([
    doctorsStore.fetchDoctors(false),
    fetchStaff(),
    specialtiesStore.fetchSpecialties(false),
    clinicServicesStore.fetchServices(false),
  ])
})

async function fetchStaff() {
  loadingStaff.value = true
  try {
    staffUsers.value = await usersService.getUsers('staff')
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to load staff accounts'
  } finally {
    loadingStaff.value = false
  }
}

// Doctor Actions
const handleCreateDoctor = async () => {
  actionError.value = null
  actionSuccess.value = null
  const normalizedPhone = doctorForm.phone
    ? normalizePhilippineMobile(doctorForm.phone)
    : null
  if (doctorForm.phone && !normalizedPhone) {
    actionError.value = 'Enter a valid Philippine mobile number, such as 0917 123 4567.'
    return
  }
  try {
    await doctorsStore.createDoctor({
      email: doctorForm.email,
      name: doctorForm.name,
      password: doctorForm.password,
      title: doctorForm.title || null,
      specialty_id: doctorForm.specialty_id || null,
      phone: normalizedPhone,
      bio: doctorForm.bio || null,
      profile_image_url: doctorForm.profile_image_url || null,
      is_active: doctorForm.is_active,
    })
    actionSuccess.value = 'Doctor account and profile created successfully'
    showDoctorModal.value = false
    // reset form
    doctorForm.email = ''
    doctorForm.name = ''
    doctorForm.password = ''
    doctorForm.title = ''
    doctorForm.specialty_id = ''
    doctorForm.phone = ''
    doctorForm.bio = ''
    doctorForm.profile_image_url = ''
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to create doctor'
  }
}

const handleDeleteDoctor = (id: string) => {
  pendingDelete.value = { type: 'doctor', id }
}

const handleCreateStaff = async () => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await usersService.createStaffUser({
      email: staffForm.email,
      name: staffForm.name,
      password: staffForm.password,
    })
    actionSuccess.value = 'Staff account created successfully'
    showStaffModal.value = false
    staffForm.email = ''
    staffForm.name = ''
    staffForm.password = ''
    await fetchStaff()
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to create staff account'
  }
}

const handleToggleStaffActive = async (staff: User) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    const updated = await usersService.toggleUserActive(staff.id)
    const index = staffUsers.value.findIndex((user) => user.id === updated.id)
    if (index !== -1) staffUsers.value[index] = updated
    actionSuccess.value = `${updated.name}'s account is now ${updated.is_active ? 'active' : 'inactive'}`
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update staff account status'
  }
}

// Specialty Actions
const openCreateSpecialty = () => {
  editingSpecialtyId.value = null
  Object.assign(specialtyForm, { name: '', description: '', is_active: true })
  showSpecialtyModal.value = true
}

const openEditSpecialty = (specialty: Specialty) => {
  editingSpecialtyId.value = specialty.id
  Object.assign(specialtyForm, {
    name: specialty.name,
    description: specialty.description || '',
    is_active: specialty.is_active,
  })
  showSpecialtyModal.value = true
}

const handleCreateSpecialty = async () => {
  actionError.value = null
  actionSuccess.value = null
  try {
    const data = {
      name: specialtyForm.name,
      description: specialtyForm.description || null,
      is_active: specialtyForm.is_active,
    }
    if (editingSpecialtyId.value) {
      await specialtiesStore.updateSpecialty(editingSpecialtyId.value, data)
      actionSuccess.value = 'Specialty updated successfully'
    } else {
      await specialtiesStore.createSpecialty(data)
      actionSuccess.value = 'Specialty created successfully'
    }
    showSpecialtyModal.value = false
    specialtyForm.name = ''
    specialtyForm.description = ''
  } catch (err: any) {
    actionError.value = err?.data?.detail || `Failed to ${editingSpecialtyId.value ? 'update' : 'create'} specialty`
  }
}

const handleDeleteSpecialty = (id: string) => {
  pendingDelete.value = { type: 'specialty', id }
}

// Service Actions
const openCreateService = () => {
  editingServiceId.value = null
  Object.assign(serviceForm, {
    name: '',
    description: '',
    specialty_id: '',
    image_url: '',
    is_active: true,
  })
  showServiceModal.value = true
}

const openEditService = (service: ClinicService) => {
  editingServiceId.value = service.id
  Object.assign(serviceForm, {
    name: service.name,
    description: service.description || '',
    specialty_id: service.specialty_id || '',
    image_url: service.image_url || '',
    is_active: service.is_active,
  })
  showServiceModal.value = true
}

const handleServiceImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  actionError.value = null
  if (!['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)) {
    actionError.value = 'Choose a JPEG, PNG, WebP, or GIF image.'
    target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    actionError.value = 'Service image must be 5MB or smaller.'
    target.value = ''
    return
  }

  uploadingImage.value = true
  try {
    const res = await uploadService.uploadImage(file)
    serviceForm.image_url = res.url
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Image upload failed'
  } finally {
    uploadingImage.value = false
    target.value = ''
  }
}

const removeServiceImage = () => {
  serviceForm.image_url = ''
}

const handleCreateService = async () => {
  actionError.value = null
  actionSuccess.value = null
  try {
    const data = {
      name: serviceForm.name,
      description: serviceForm.description || null,
      specialty_id: serviceForm.specialty_id || null,
      image_url: serviceForm.image_url || null,
      is_active: serviceForm.is_active,
    }
    if (editingServiceId.value) {
      await clinicServicesStore.updateService(editingServiceId.value, data)
      actionSuccess.value = 'Clinic service updated successfully'
    } else {
      await clinicServicesStore.createService(data)
      actionSuccess.value = 'Clinic service created successfully'
    }
    showServiceModal.value = false
    serviceForm.name = ''
    serviceForm.description = ''
    serviceForm.specialty_id = ''
    serviceForm.image_url = ''
  } catch (err: any) {
    actionError.value = err?.data?.detail || `Failed to ${editingServiceId.value ? 'update' : 'create'} service`
  }
}

const handleDeleteService = (id: string) => {
  pendingDelete.value = { type: 'service', id }
}

const confirmDelete = async () => {
  const target = pendingDelete.value
  if (!target) return
  actionError.value = null
  actionSuccess.value = null
  deletingRecord.value = true
  try {
    if (target.type === 'doctor') {
      await doctorsStore.deleteDoctor(target.id)
      actionSuccess.value = 'Doctor deleted successfully'
    } else if (target.type === 'specialty') {
      await specialtiesStore.deleteSpecialty(target.id)
      actionSuccess.value = 'Specialty deleted successfully'
    } else {
      await clinicServicesStore.deleteService(target.id)
      actionSuccess.value = 'Clinic service deleted successfully'
    }
    pendingDelete.value = null
  } catch (err: any) {
    actionError.value = err?.data?.detail || `Failed to delete ${target.type}`
  } finally {
    deletingRecord.value = false
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <BasePageHeader
      title="Admin Management Portal"
      description="Create doctor and staff accounts, and manage clinic domains"
    />

    <!-- Alert Notifications -->
    <div v-if="actionSuccess" class="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideCheckCircle2 class="h-5 w-5 text-green-500" />
        <span>{{ actionSuccess }}</span>
      </div>
      <button class="text-green-700 font-bold" @click="actionSuccess = null">&times;</button>
    </div>

    <div v-if="actionError" class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideAlertCircle class="h-5 w-5 text-red-500" />
        <span>{{ actionError }}</span>
      </div>
      <button class="text-red-700 font-bold" @click="actionError = null">&times;</button>
    </div>

    <!-- Management Navigation Tabs -->
    <div class="border-b border-gray-200 mb-6 flex flex-wrap gap-2 sm:gap-4">
      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'doctors' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="activeTab = 'doctors'"
      >
        <LucideStethoscope class="h-4 w-4" />
        <span>Doctors ({{ doctorsStore.doctors.length }})</span>
      </button>

      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'staff' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="activeTab = 'staff'"
      >
        <LucideUsers class="h-4 w-4" />
        <span>Staff ({{ staffUsers.length }})</span>
      </button>

      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'specialties' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="activeTab = 'specialties'"
      >
        <LucideAward class="h-4 w-4" />
        <span>Specialties ({{ specialtiesStore.specialties.length }})</span>
      </button>

      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'services' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="activeTab = 'services'"
      >
        <LucideHeartHandshake class="h-4 w-4" />
        <span>Services ({{ clinicServicesStore.services.length }})</span>
      </button>
    </div>

    <!-- TAB 1: DOCTOR MANAGEMENT -->
    <div v-if="activeTab === 'doctors'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Doctor Profiles</h2>
        <NuxtLink to="/admin/forms/doctors/new" class="btn btn-primary">
          <LucidePlus class="h-4 w-4" />
          <span>Add Doctor</span>
        </NuxtLink>
      </div>

      <div class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
            <tr>
              <th class="px-4 py-3">Doctor</th>
              <th class="px-4 py-3">Specialty</th>
              <th class="px-4 py-3">Phone</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="doc in doctorsStore.doctors" :key="doc.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900 flex items-center gap-3">
                <div class="h-9 w-9 rounded-full overflow-hidden bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0 ring-1 ring-gray-200">
                  <BaseAvatar :src="doc.profile_image_url" :alt="`${doc.user.name} avatar`" />
                </div>
                <div>
                  <div>Dr. {{ doc.user.name }} <span v-if="doc.title" class="text-xs text-gray-500">({{ doc.title }})</span></div>
                  <div class="text-xs text-gray-500">{{ doc.user.email }}</div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span v-if="doc.specialty" class="inline-block px-2 py-0.5 rounded text-xs bg-teal-50 text-teal-700 font-medium">
                  {{ doc.specialty.name }}
                </span>
                <span v-else class="text-gray-400 text-xs">Unassigned</span>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ doc.phone || '-' }}</td>
              <td class="px-4 py-3">
                <span :class="doc.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'" class="px-2 py-0.5 rounded text-xs font-medium">
                  {{ doc.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button class="text-red-600 hover:text-red-800 text-xs font-medium" @click="handleDeleteDoctor(doc.id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 2: STAFF MANAGEMENT -->
    <div v-if="activeTab === 'staff'" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Staff Accounts</h2>
          <p class="text-xs text-gray-500">Create staff accounts and manage their access.</p>
        </div>
        <NuxtLink to="/admin/forms/staff/new" class="btn btn-primary">
          <LucideUserPlus class="h-4 w-4" />
          <span>Add Staff</span>
        </NuxtLink>
      </div>

      <div v-if="loadingStaff" class="flex justify-center py-12">
        <LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" />
      </div>

      <div v-else class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="border-b border-gray-200 bg-gray-50 font-semibold text-gray-700">
            <tr>
              <th class="px-4 py-3">Staff Member</th>
              <th class="px-4 py-3">Email Verification</th>
              <th class="px-4 py-3">Account Status</th>
              <th class="px-4 py-3">Created</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="staff in staffUsers" :key="staff.id" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                    <BaseAvatar :src="staff.profile_image_url" :alt="`${staff.name} avatar`" />
                  </div>
                  <div>
                    <div class="font-semibold text-gray-900">{{ staff.name }}</div>
                    <div class="text-xs text-gray-500">{{ staff.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3"><BaseStatusBadge :status="staff.is_email_verified ? 'Verified' : 'Unverified'" /></td>
              <td class="px-4 py-3"><BaseStatusBadge :status="staff.is_active ? 'Active' : 'Deactivated'" /></td>
              <td class="px-4 py-3 text-gray-600">{{ new Date(staff.created_at).toLocaleDateString() }}</td>
              <td class="px-4 py-3 text-right">
                <button
                  class="text-xs font-medium"
                  :class="staff.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'"
                  @click="handleToggleStaffActive(staff)"
                >
                  {{ staff.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </td>
            </tr>
            <tr v-if="staffUsers.length === 0">
              <td colspan="5" class="px-4 py-10 text-center text-sm text-gray-500">No staff accounts yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 3: SPECIALTY MANAGEMENT -->
    <div v-if="activeTab === 'specialties'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Medical Specialties</h2>
        <NuxtLink to="/admin/forms/specialties/new" class="btn btn-primary">
          <LucidePlus class="h-4 w-4" />
          <span>Add Specialty</span>
        </NuxtLink>
      </div>

      <div class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
            <tr>
              <th class="px-4 py-3">Name</th>
              <th class="px-4 py-3">Description</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="s in specialtiesStore.specialties" :key="s.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-semibold text-gray-900">{{ s.name }}</td>
              <td class="px-4 py-3 text-gray-600 max-w-xs truncate">{{ s.description || '-' }}</td>
              <td class="px-4 py-3">
                <span :class="s.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'" class="px-2 py-0.5 rounded text-xs font-medium">
                  {{ s.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right space-x-3">
                <NuxtLink :to="`/admin/forms/specialties/${s.id}`" class="text-primary-600 hover:text-primary-800 text-xs font-medium">
                  Edit
                </NuxtLink>
                <button class="text-red-600 hover:text-red-800 text-xs font-medium" @click="handleDeleteSpecialty(s.id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: SERVICE MANAGEMENT -->
    <div v-if="activeTab === 'services'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Clinic Services</h2>
        <NuxtLink to="/admin/forms/services/new" class="btn btn-primary">
          <LucidePlus class="h-4 w-4" />
          <span>Add Service</span>
        </NuxtLink>
      </div>

      <div class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
            <tr>
              <th class="px-4 py-3">Service</th>
              <th class="px-4 py-3">Specialty</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="srv in clinicServicesStore.services" :key="srv.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-semibold text-gray-900 flex items-center gap-3">
                <img :src="srv.image_url || '/images/default-service.svg'" :alt="`${srv.name} cover`" class="h-8 w-8 rounded object-cover border border-gray-200" @error="($event.target as HTMLImageElement).src = '/images/default-service.svg'" />
                <span>{{ srv.name }}</span>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ srv.specialty?.name || '-' }}</td>
              <td class="px-4 py-3">
                <span :class="srv.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'" class="px-2 py-0.5 rounded text-xs font-medium">
                  {{ srv.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right space-x-3">
                <NuxtLink :to="`/admin/forms/services/${srv.id}`" class="text-primary-600 hover:text-primary-800 text-xs font-medium">
                  Edit
                </NuxtLink>
                <button class="text-red-600 hover:text-red-800 text-xs font-medium" @click="handleDeleteService(srv.id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: ADD STAFF -->
    <div v-if="showStaffModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Create staff account" @click.self="showStaffModal = false">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Create Staff Account</h3>
        <p class="text-sm text-gray-600">The staff member can sign in immediately using these credentials.</p>

        <form class="space-y-3" @submit.prevent="handleCreateStaff">
          <div>
            <label class="form-label">Full Name</label>
            <input v-model.trim="staffForm.name" type="text" required maxlength="255" autocomplete="name" placeholder="John Doe" class="form-input" />
          </div>
          <div>
            <label class="form-label">Email Address</label>
            <input v-model.trim="staffForm.email" type="email" required autocomplete="email" placeholder="staff@example.com" class="form-input" />
          </div>
          <div>
            <label class="form-label">Temporary Password</label>
            <input v-model="staffForm.password" type="password" required minlength="8" maxlength="128" autocomplete="new-password" placeholder="At least 8 characters" class="form-input" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showStaffModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary">Create Staff</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: ADD DOCTOR -->
    <div v-if="showDoctorModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add doctor account and profile" @click.self="showDoctorModal = false">
      <div class="modal-panel max-w-lg space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Add Doctor Account & Profile</h3>

        <form class="space-y-3" @submit.prevent="handleCreateDoctor">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Doctor Name</label>
            <input v-model="doctorForm.name" type="text" required placeholder="Dr. Jane Smith" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Email Address</label>
            <input v-model="doctorForm.email" type="email" required placeholder="doctor@example.com" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Temporary Password</label>
            <input v-model="doctorForm.password" type="password" required minlength="8" placeholder="••••••••" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>

          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Title/Credentials</label>
              <input v-model="doctorForm.title" type="text" placeholder="MD, FACP" class="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Specialty</label>
              <select v-model="doctorForm.specialty_id" class="w-full px-3 py-2 border rounded-lg text-sm">
                <option value="">Select Specialty</option>
                <option v-for="s in specialtiesStore.specialties" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Mobile Number (Philippines)</label>
            <input v-model="doctorForm.phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="0917 123 4567" class="form-input" />
            <p class="mt-1 text-xs text-gray-500">Use 09XXXXXXXXX or +639XXXXXXXXX.</p>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Biography</label>
            <textarea v-model="doctorForm.bio" rows="3" placeholder="Doctor biography..." class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showDoctorModal = false">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">Save Doctor</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: ADD SPECIALTY -->
    <div v-if="showSpecialtyModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add medical specialty" @click.self="showSpecialtyModal = false">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">{{ editingSpecialtyId ? 'Edit Medical Specialty' : 'Add Medical Specialty' }}</h3>

        <form class="space-y-3" @submit.prevent="handleCreateSpecialty">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Specialty Name</label>
            <input v-model="specialtyForm.name" type="text" required placeholder="Cardiology" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>

          <label class="flex items-center gap-2 text-xs font-medium text-gray-700">
            <input v-model="specialtyForm.is_active" type="checkbox" class="h-4 w-4 rounded text-primary-600" />
            Active specialty
          </label>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="specialtyForm.description" rows="3" placeholder="Department description..." class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showSpecialtyModal = false">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
              {{ editingSpecialtyId ? 'Update Specialty' : 'Save Specialty' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: ADD SERVICE -->
    <div v-if="showServiceModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add clinic service" @click.self="showServiceModal = false">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">{{ editingServiceId ? 'Edit Clinic Service' : 'Add Clinic Service' }}</h3>

        <form class="space-y-3" @submit.prevent="handleCreateService">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Service Name</label>
            <input v-model="serviceForm.name" type="text" required placeholder="General Consultation" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Associated Specialty</label>
            <select v-model="serviceForm.specialty_id" class="w-full px-3 py-2 border rounded-lg text-sm">
              <option value="">Select Specialty (Optional)</option>
              <option v-for="s in specialtiesStore.specialties" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>

          <div>
            <label class="form-label">Service Image</label>
            <div class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
              <div class="relative flex aspect-[16/7] items-center justify-center overflow-hidden bg-gradient-to-br from-primary-50 via-white to-teal-50">
                <img
                  :src="serviceForm.image_url || '/images/default-service.svg'"
                  :alt="`${serviceForm.name || 'Clinic service'} preview`"
                  class="h-full w-full object-cover"
                  @error="($event.target as HTMLImageElement).src = '/images/default-service.svg'"
                />

                <div v-if="uploadingImage" class="absolute inset-0 flex flex-col items-center justify-center bg-white/85 backdrop-blur-sm">
                  <LucideLoader2 class="h-7 w-7 animate-spin text-primary-600" />
                  <span class="mt-2 text-xs font-semibold text-primary-700">Uploading image...</span>
                </div>
              </div>

              <div class="flex flex-col gap-3 border-t border-slate-200 bg-white p-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="text-xs font-medium text-gray-700">Recommended: landscape image</p>
                  <p class="text-[11px] text-gray-500">JPEG, PNG, WebP or GIF · maximum 5MB</p>
                </div>
                <div class="flex gap-2">
                  <button
                    v-if="serviceForm.image_url"
                    type="button"
                    class="btn btn-ghost text-red-600 hover:bg-red-50 hover:text-red-700"
                    :disabled="uploadingImage"
                    @click="removeServiceImage"
                  >
                    <LucideTrash2 class="h-4 w-4" />
                    <span>Remove</span>
                  </button>
                  <label class="btn btn-secondary cursor-pointer px-4 py-2">
                    <LucideUpload class="h-4 w-4" />
                    <span>{{ serviceForm.image_url ? 'Replace Image' : 'Choose Image' }}</span>
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp,image/gif"
                      class="hidden"
                      :disabled="uploadingImage"
                      @change="handleServiceImageUpload"
                    />
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="serviceForm.description" rows="3" placeholder="Service overview..." class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
          </div>

          <label class="flex items-center gap-2 text-xs font-medium text-gray-700">
            <input v-model="serviceForm.is_active" type="checkbox" class="h-4 w-4 rounded text-primary-600" />
            Active service
          </label>

          <div class="modal-actions">
            <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showServiceModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="uploadingImage">
              {{ editingServiceId ? 'Update Service' : 'Save Service' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <BaseConfirmModal
      :model-value="Boolean(pendingDelete)"
      :title="deleteModalCopy[0]"
      :description="deleteModalCopy[1]"
      :confirm-label="deleteModalCopy[2]"
      :loading="deletingRecord"
      @update:model-value="!$event && (pendingDelete = null)"
      @confirm="confirmDelete"
    />
  </div>
</template>
