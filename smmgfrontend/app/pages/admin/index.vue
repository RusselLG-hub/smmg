<script setup lang="ts">
import { computed, ref, reactive, onMounted, watch } from 'vue'
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
import type { PatientProfile } from '~~/shared/types/Patient'
import { usePatientService } from '~/services/patient'
import { useAppointmentsService } from '~/services/appointments'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({
  middleware: 'auth',
})

const doctorsStore = useDoctorsStore()
const specialtiesStore = useSpecialtiesStore()
const clinicServicesStore = useClinicServicesStore()
const uploadService = useUploadService()
const usersService = useUsersService()
const patientService = usePatientService()
const appointmentsService = useAppointmentsService()

const route = useRoute()
const requestedTab = String(route.query.tab || '')
const activeTab = ref<'doctors' | 'staff' | 'specialties' | 'services' | 'patients'>(
  ['doctors', 'staff', 'specialties', 'services', 'patients'].includes(requestedTab)
    ? requestedTab as 'doctors' | 'staff' | 'specialties' | 'services' | 'patients'
    : 'doctors',
)
watch(
  () => route.query.tab,
  (tab) => {
    const value = String(tab || '')
    if (['doctors', 'staff', 'specialties', 'services', 'patients'].includes(value)) {
      activeTab.value = value as typeof activeTab.value
    }
  },
)
const staffUsers = ref<User[]>([])
const loadingStaff = ref(false)
const patientRecords = ref<PatientProfile[]>([])
const loadingPatients = ref(false)
const patientSearch = ref('')
const patientStatusFilter = ref('')
const patientViewMode = ref<'active' | 'archived'>('active')
const selectedPatientRecord = ref<PatientProfile | null>(null)
const patientAppointments = ref<Appointment[]>([])
const loadingPatientHistory = ref(false)
const pendingArchivePatient = ref<PatientProfile | null>(null)
const archivingPatient = ref(false)

const activePatientRecords = computed(() => patientRecords.value.filter(p => p.user.is_active))
const archivedPatientRecords = computed(() => patientRecords.value.filter(p => !p.user.is_active))

const filteredPatientRecords = computed(() => {
  const base = patientViewMode.value === 'active' ? activePatientRecords.value : archivedPatientRecords.value
  return base.filter(patient => {
    if (patientStatusFilter.value) {
      const matchLatest = patient.appointment_status === patientStatusFilter.value
      const matchAll = Boolean(patient.all_statuses?.includes(patientStatusFilter.value))
      if (!matchLatest && !matchAll) return false
    }

    const query = patientSearch.value.trim().toLowerCase()
    if (!query) return true

    return (
      patient.user.name.toLowerCase().includes(query)
      || patient.user.email.toLowerCase().includes(query)
      || (patient.phone || '').toLowerCase().includes(query)
      || (patient.doctor?.name || '').toLowerCase().includes(query)
      || (patient.doctor?.specialty_name || '').toLowerCase().includes(query)
    )
  })
})

const showDoctorModal = ref(false)
const showStaffModal = ref(false)
const showSpecialtyModal = ref(false)
const showServiceModal = ref(false)
const editingSpecialtyId = ref<string | null>(null)
const editingServiceId = ref<string | null>(null)

const actionError = ref<string | null>(null)
const actionSuccess = ref<string | null>(null)
const uploadingImage = ref(false)
type DeleteTarget = { type: 'doctor' | 'specialty' | 'service' | 'patient'; id: string }
const pendingDelete = ref<DeleteTarget | null>(null)
const deletingRecord = ref(false)

const deleteModalCopy = computed(() => {
  const labels = {
    doctor: ['Delete doctor account?', 'The doctor account and associated profile will be permanently removed.', 'Delete Doctor'],
    specialty: ['Delete specialty?', 'This specialty will be permanently removed from the clinic catalog.', 'Delete Specialty'],
    service: ['Delete clinic service?', 'This service will be permanently removed from the public catalog.', 'Delete Service'],
    patient: ['Permanently delete patient record?', 'This patient profile, account, and all associated appointment records will be permanently removed.', 'Permanently Delete Patient'],
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
    fetchPatients(),
    specialtiesStore.fetchSpecialties(false),
    clinicServicesStore.fetchServices(false),
  ])
})

async function fetchPatients() {
  loadingPatients.value = true
  try {
    patientRecords.value = await patientService.getPatientRecords()
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to load patient records'
  } finally {
    loadingPatients.value = false
  }
}

async function openPatientRecord(patient: PatientProfile) {
  selectedPatientRecord.value = patient
  loadingPatientHistory.value = true
  try {
    patientAppointments.value = await appointmentsService.getAdminAppointments({ patient_id: patient.id })
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to load patient appointment history'
    patientAppointments.value = []
  } finally {
    loadingPatientHistory.value = false
  }
}

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
    } else if (target.type === 'service') {
      await clinicServicesStore.deleteService(target.id)
      actionSuccess.value = 'Clinic service deleted successfully'
    } else if (target.type === 'patient') {
      await patientService.deletePatient(target.id)
      patientRecords.value = patientRecords.value.filter(p => p.id !== target.id)
      actionSuccess.value = 'Patient record permanently deleted successfully'
    }
    pendingDelete.value = null
  } catch (err: any) {
    actionError.value = err?.data?.detail || `Failed to delete ${target.type}`
  } finally {
    deletingRecord.value = false
  }
}

const handleArchivePatient = (patient: PatientProfile) => {
  pendingArchivePatient.value = patient
}

const confirmArchivePatient = async () => {
  if (!pendingArchivePatient.value) return
  archivingPatient.value = true
  actionError.value = null
  actionSuccess.value = null
  try {
    const updated = await patientService.archivePatient(pendingArchivePatient.value.id)
    const index = patientRecords.value.findIndex(p => p.id === updated.id)
    if (index !== -1) {
      patientRecords.value[index] = updated
    }
    actionSuccess.value = `Patient ${updated.user.name} archived successfully.`
    pendingArchivePatient.value = null
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to archive patient record'
  } finally {
    archivingPatient.value = false
  }
}

const handleRestorePatient = async (patient: PatientProfile) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    const updated = await patientService.restorePatient(patient.id)
    const index = patientRecords.value.findIndex(p => p.id === updated.id)
    if (index !== -1) {
      patientRecords.value[index] = updated
    }
    actionSuccess.value = `Patient ${updated.user.name} restored successfully.`
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to restore patient record'
  }
}

const handlePermanentlyDeletePatient = (patient: PatientProfile) => {
  pendingDelete.value = { type: 'patient', id: patient.id }
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

      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'patients' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="activeTab = 'patients'"
      >
        <LucideFolderHeart class="h-4 w-4" />
        <span>Patient Records ({{ patientRecords.length }})</span>
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

    <!-- TAB 5: PATIENT RECORD MANAGEMENT -->
    <div v-if="activeTab === 'patients'" class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Patient Record Management</h2>
          <p class="text-xs text-gray-500">View registered patient profiles, handling doctors, and appointment records.</p>
        </div>
        <!-- Active / Archived Toggle -->
        <div class="inline-flex rounded-lg bg-gray-100 p-1 text-xs font-semibold">
          <button
            type="button"
            class="px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5"
            :class="patientViewMode === 'active' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
            @click="patientViewMode = 'active'"
          >
            <LucideUsers class="h-3.5 w-3.5" />
            <span>Active Patients ({{ activePatientRecords.length }})</span>
          </button>
          <button
            type="button"
            class="px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5"
            :class="patientViewMode === 'archived' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
            @click="patientViewMode = 'archived'"
          >
            <LucideArchive class="h-3.5 w-3.5" />
            <span>Archived ({{ archivedPatientRecords.length }})</span>
          </button>
        </div>
      </div>

      <!-- Filters: Search and Status Filter (confirmed, pending, cancel) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl">
        <div class="sm:col-span-2">
          <label class="form-label">Search Patients</label>
          <div class="relative">
            <LucideSearch class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              v-model="patientSearch"
              class="form-input pl-9"
              placeholder="Search by patient, doctor, email, or phone"
            />
          </div>
        </div>
        <div>
          <label class="form-label">Status Filter</label>
          <select v-model="patientStatusFilter" class="form-input">
            <option value="">All Statuses</option>
            <option value="confirmed">Confirmed</option>
            <option value="pending">Pending</option>
            <option value="cancelled">Cancel</option>
          </select>
        </div>
      </div>

      <div v-if="loadingPatients" class="flex justify-center py-12">
        <LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" />
      </div>

      <div v-else class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="border-b border-gray-200 bg-gray-50 font-semibold">
            <tr>
              <th class="px-4 py-3">Patient</th>
              <th class="px-4 py-3">Doctor</th>
              <th class="px-4 py-3">Contact</th>
              <th class="px-4 py-3">Demographics</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="patient in filteredPatientRecords" :key="patient.id" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="font-semibold text-gray-900">{{ patient.user.name }}</div>
                <div class="text-xs text-gray-500">{{ patient.user.email }}</div>
              </td>
              <td class="px-4 py-3">
                <div v-if="patient.doctor" class="flex items-center gap-2">
                  <div class="h-7 w-7 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0">
                    Dr
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">Dr. {{ patient.doctor.name }}</div>
                    <div class="text-xs text-gray-500">{{ patient.doctor.specialty_name || patient.doctor.title || 'General Practice' }}</div>
                  </div>
                </div>
                <span v-else class="text-xs text-gray-400 italic">No doctor assigned</span>
              </td>
              <td class="px-4 py-3">{{ patient.phone || 'Not provided' }}</td>
              <td class="px-4 py-3">
                <div>{{ patient.gender || 'Not provided' }}</div>
                <div class="text-xs text-gray-500">Born: {{ patient.date_of_birth || 'Not provided' }}</div>
              </td>
              <td class="px-4 py-3">
                <BaseStatusBadge v-if="patient.appointment_status" :status="patient.appointment_status" />
                <span v-else class="text-xs text-gray-400 italic">No appointment</span>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    class="text-xs font-semibold text-primary-700 hover:text-primary-900 hover:underline"
                    @click="openPatientRecord(patient)"
                  >
                    View Record
                  </button>

                  <!-- When in active view: Archive button -->
                  <button
                    v-if="patientViewMode === 'active'"
                    type="button"
                    class="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 hover:text-amber-900 hover:underline"
                    title="Archive patient"
                    @click="handleArchivePatient(patient)"
                  >
                    <LucideArchive class="h-3.5 w-3.5" />
                    <span>Archive</span>
                  </button>

                  <!-- When in archive view: Restore & Permanently Delete options -->
                  <template v-else>
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 hover:text-emerald-900 hover:underline"
                      title="Restore patient record"
                      @click="handleRestorePatient(patient)"
                    >
                      <LucideRotateCcw class="h-3.5 w-3.5" />
                      <span>Restore</span>
                    </button>
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 text-xs font-semibold text-red-600 hover:text-red-800 hover:underline"
                      title="Permanently delete patient record"
                      @click="handlePermanentlyDeletePatient(patient)"
                    >
                      <LucideTrash2 class="h-3.5 w-3.5" />
                      <span>Permanently Delete</span>
                    </button>
                  </template>
                </div>
              </td>
            </tr>
            <tr v-if="filteredPatientRecords.length === 0">
              <td colspan="6" class="px-4 py-10 text-center text-gray-500">
                {{ patientViewMode === 'active' ? 'No active patient records match your filter or search.' : 'No archived patient records found.' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: ARCHIVE PATIENT CONFIRMATION -->
    <div
      v-if="pendingArchivePatient"
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Archive patient record"
      @click.self="pendingArchivePatient = null"
    >
      <div class="modal-panel max-w-md space-y-4">
        <div class="flex items-center gap-3 text-amber-600">
          <div class="rounded-full bg-amber-100 p-2">
            <LucideArchive class="h-6 w-6" />
          </div>
          <h3 class="text-lg font-bold text-gray-900">Archive Patient Record?</h3>
        </div>
        <p class="text-sm text-gray-600">
          Are you sure you want to archive <strong>{{ pendingArchivePatient.user.name }}</strong>? The record will be moved to the archive section, where it can be restored or permanently deleted at any time.
        </p>
        <div class="modal-actions">
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="archivingPatient"
            @click="pendingArchivePatient = null"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-warning px-4 py-2"
            :disabled="archivingPatient"
            @click="confirmArchivePatient"
          >
            <LucideLoader2 v-if="archivingPatient" class="h-4 w-4 animate-spin" />
            <LucideArchive v-else class="h-4 w-4" />
            <span>Archive Patient</span>
          </button>
        </div>
      </div>
    </div>

    <BaseModal :model-value="Boolean(selectedPatientRecord)" title="Patient Record" description="Profile details and appointment history" max-width="xl" @update:model-value="!$event && (selectedPatientRecord = null)">
      <div v-if="selectedPatientRecord" class="space-y-6">
        <div class="grid gap-4 rounded-xl bg-gray-50 p-4 text-sm sm:grid-cols-2">
          <div><p class="text-xs font-semibold uppercase text-gray-500">Patient</p><p class="mt-1 font-bold text-gray-900">{{ selectedPatientRecord.user.name }}</p><p class="text-gray-600">{{ selectedPatientRecord.user.email }}</p></div>
          <div><p class="text-xs font-semibold uppercase text-gray-500">Handling Doctor</p><p class="mt-1 font-bold text-gray-900">{{ selectedPatientRecord.doctor ? `Dr. ${selectedPatientRecord.doctor.name}` : 'No doctor assigned' }}</p><p v-if="selectedPatientRecord.doctor" class="text-gray-600">{{ selectedPatientRecord.doctor.specialty_name || selectedPatientRecord.doctor.title || '' }}</p></div>
          <div><p class="text-xs font-semibold uppercase text-gray-500">Contact</p><p class="mt-1 text-gray-900">{{ selectedPatientRecord.phone || 'Not provided' }}</p></div>
          <div><p class="text-xs font-semibold uppercase text-gray-500">Demographics</p><p class="mt-1 text-gray-900">{{ selectedPatientRecord.gender || 'Not provided' }} · Born {{ selectedPatientRecord.date_of_birth || 'Not provided' }}</p></div>
          <div class="sm:col-span-2"><p class="text-xs font-semibold uppercase text-gray-500">Address</p><p class="mt-1 text-gray-900">{{ selectedPatientRecord.address || 'Not provided' }}</p></div>
        </div>
        <div><h3 class="font-bold text-gray-900">Appointment History</h3><p class="text-xs text-gray-500">All recorded appointments for this patient.</p></div>
        <div v-if="loadingPatientHistory" class="flex justify-center py-8"><LucideLoader2 class="h-6 w-6 animate-spin text-primary-600" /></div>
        <div v-else class="space-y-2">
          <div v-for="appointment in patientAppointments" :key="appointment.id" class="flex flex-col gap-2 rounded-xl border border-gray-200 p-3 text-sm sm:flex-row sm:items-center sm:justify-between">
            <div><p class="font-semibold text-gray-900">{{ appointment.service?.name || 'General consultation' }} with Dr. {{ appointment.doctor.user.name }}</p><p class="text-xs text-gray-500">{{ new Date(appointment.scheduled_at).toLocaleString() }} · {{ appointment.appointment_reference }}</p></div>
            <BaseStatusBadge :status="appointment.status" />
          </div>
          <p v-if="patientAppointments.length === 0" class="py-6 text-center text-sm text-gray-500">No appointment history recorded.</p>
        </div>
      </div>
    </BaseModal>

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
