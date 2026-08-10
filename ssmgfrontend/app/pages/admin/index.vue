<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useDoctorsStore } from '~/stores/doctors'
import { useSpecialtiesStore } from '~/stores/specialties'
import { useClinicServicesStore } from '~/stores/clinicServices'
import { useUploadService } from '~/services/upload'
import { normalizePhilippineMobile } from '~/utils/phone'
import type { Doctor } from '~~/shared/types/Doctor'
import type { Specialty } from '~~/shared/types/Specialty'
import type { ClinicService } from '~~/shared/types/ClinicService'

definePageMeta({
  middleware: 'auth',
})

const doctorsStore = useDoctorsStore()
const specialtiesStore = useSpecialtiesStore()
const clinicServicesStore = useClinicServicesStore()
const uploadService = useUploadService()

const activeTab = ref<'doctors' | 'specialties' | 'services'>('doctors')

const showDoctorModal = ref(false)
const showSpecialtyModal = ref(false)
const showServiceModal = ref(false)

const actionError = ref<string | null>(null)
const actionSuccess = ref<string | null>(null)
const uploadingImage = ref(false)

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
    specialtiesStore.fetchSpecialties(false),
    clinicServicesStore.fetchServices(false),
  ])
})

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

const handleDeleteDoctor = async (id: string) => {
  if (!confirm('Are you sure you want to delete this doctor account?')) return
  try {
    await doctorsStore.deleteDoctor(id)
    actionSuccess.value = 'Doctor deleted successfully'
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to delete doctor'
  }
}

// Specialty Actions
const handleCreateSpecialty = async () => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await specialtiesStore.createSpecialty({
      name: specialtyForm.name,
      description: specialtyForm.description || null,
      is_active: specialtyForm.is_active,
    })
    actionSuccess.value = 'Specialty created successfully'
    showSpecialtyModal.value = false
    specialtyForm.name = ''
    specialtyForm.description = ''
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to create specialty'
  }
}

const handleDeleteSpecialty = async (id: string) => {
  if (!confirm('Are you sure you want to delete this specialty?')) return
  try {
    await specialtiesStore.deleteSpecialty(id)
    actionSuccess.value = 'Specialty deleted successfully'
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to delete specialty'
  }
}

// Service Actions
const handleServiceImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  uploadingImage.value = true
  try {
    const res = await uploadService.uploadImage(target.files[0])
    serviceForm.image_url = res.url
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Image upload failed'
  } finally {
    uploadingImage.value = false
  }
}

const handleCreateService = async () => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await clinicServicesStore.createService({
      name: serviceForm.name,
      description: serviceForm.description || null,
      specialty_id: serviceForm.specialty_id || null,
      image_url: serviceForm.image_url || null,
      is_active: serviceForm.is_active,
    })
    actionSuccess.value = 'Clinic service created successfully'
    showServiceModal.value = false
    serviceForm.name = ''
    serviceForm.description = ''
    serviceForm.specialty_id = ''
    serviceForm.image_url = ''
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to create service'
  }
}

const handleDeleteService = async (id: string) => {
  if (!confirm('Are you sure you want to delete this service?')) return
  try {
    await clinicServicesStore.deleteService(id)
    actionSuccess.value = 'Clinic service deleted successfully'
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to delete service'
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <BasePageHeader
      title="Admin Management Portal"
      description="Manage doctors, specialties, and clinic services"
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
    <div class="border-b border-gray-200 mb-6 flex gap-4">
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
        <button
          class="btn btn-primary"
          @click="showDoctorModal = true"
        >
          <LucidePlus class="h-4 w-4" />
          <span>Add New Doctor</span>
        </button>
      </div>

      <div class="card overflow-x-auto">
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
                <div class="h-8 w-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0">
                  {{ doc.user.name.charAt(0) }}
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

    <!-- TAB 2: SPECIALTY MANAGEMENT -->
    <div v-if="activeTab === 'specialties'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Medical Specialties</h2>
        <button
          class="btn btn-primary"
          @click="showSpecialtyModal = true"
        >
          <LucidePlus class="h-4 w-4" />
          <span>Add Specialty</span>
        </button>
      </div>

      <div class="card overflow-x-auto">
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
              <td class="px-4 py-3 text-right">
                <button class="text-red-600 hover:text-red-800 text-xs font-medium" @click="handleDeleteSpecialty(s.id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 3: SERVICE MANAGEMENT -->
    <div v-if="activeTab === 'services'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">Clinic Services</h2>
        <button
          class="btn btn-primary"
          @click="showServiceModal = true"
        >
          <LucidePlus class="h-4 w-4" />
          <span>Add Service</span>
        </button>
      </div>

      <div class="card overflow-x-auto">
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
                <img v-if="srv.image_url" :src="srv.image_url" class="h-8 w-8 rounded object-cover border border-gray-200" />
                <span>{{ srv.name }}</span>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ srv.specialty?.name || '-' }}</td>
              <td class="px-4 py-3">
                <span :class="srv.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'" class="px-2 py-0.5 rounded text-xs font-medium">
                  {{ srv.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button class="text-red-600 hover:text-red-800 text-xs font-medium" @click="handleDeleteService(srv.id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: ADD DOCTOR -->
    <div v-if="showDoctorModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add doctor account and profile">
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
    <div v-if="showSpecialtyModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add medical specialty">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Add Medical Specialty</h3>

        <form class="space-y-3" @submit.prevent="handleCreateSpecialty">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Specialty Name</label>
            <input v-model="specialtyForm.name" type="text" required placeholder="Cardiology" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="specialtyForm.description" rows="3" placeholder="Department description..." class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showSpecialtyModal = false">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">Save Specialty</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: ADD SERVICE -->
    <div v-if="showServiceModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add clinic service">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Add Clinic Service</h3>

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
            <label class="block text-xs font-medium text-gray-700 mb-1">Service Image</label>
            <input type="file" accept="image/*" class="w-full text-xs" @change="handleServiceImageUpload" />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="serviceForm.description" rows="3" placeholder="Service overview..." class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showServiceModal = false">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">Save Service</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
