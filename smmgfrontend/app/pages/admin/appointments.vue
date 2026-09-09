<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import { useDoctorsStore } from '~/stores/doctors'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({
  middleware: 'auth',
})

const appointmentsStore = useAppointmentsStore()
const doctorsStore = useDoctorsStore()

const todayStr = new Date().toISOString().split('T')[0]
const filterDoctorId = ref<string>('')
const filterStatus = ref<string>('')
const filterDate = ref<string>('')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)
const selectedPatientAppointment = ref<Appointment | null>(null)

onMounted(async () => {
  await Promise.all([
    doctorsStore.fetchDoctors(false),
    appointmentsStore.fetchAdminAppointments(),
  ])
})

watch([filterDoctorId, filterStatus, filterDate], async () => {
  await appointmentsStore.fetchAdminAppointments({
    doctor_id: filterDoctorId.value || undefined,
    status: filterStatus.value || undefined,
    date: filterDate.value || undefined,
  })
})

const handleUpdateStatus = async (id: string, newStatus: string) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await appointmentsStore.updateStatus(id, newStatus)
    actionSuccess.value = `Status updated to ${newStatus}.`
    await appointmentsStore.fetchAdminAppointments({
      doctor_id: filterDoctorId.value || undefined,
      status: filterStatus.value || undefined,
      date: filterDate.value || undefined,
    })
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update status.'
  }
}

const formatDate = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

const formatTime = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <BasePageHeader
      title="Clinic Appointments Directory"
      description="All clinic bookings and consultations with flexible doctor, status, and date filters"
    />

    <!-- Filter Controls Card -->
    <div class="card mb-6 p-5 sm:p-6 shadow-sm">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <label class="form-label text-xs mb-1.5">Doctor</label>
          <select v-model="filterDoctorId" class="form-input w-full text-xs">
            <option value="">All Doctors</option>
            <option v-for="d in doctorsStore.doctors" :key="d.id" :value="d.id">Dr. {{ d.user.name }}</option>
          </select>
        </div>

        <div>
          <label class="form-label text-xs mb-1.5">Status</label>
          <select v-model="filterStatus" class="form-input w-full text-xs">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="form-label mb-0 text-xs">Filter Date</label>
            <button
              v-if="filterDate"
              type="button"
              class="text-[11px] font-semibold text-primary-600 hover:text-primary-800 hover:underline"
              @click="filterDate = ''"
            >
              Clear (All Dates)
            </button>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="filterDate" type="date" class="form-input min-w-0 flex-1 text-xs" />
            <button
              type="button"
              class="px-3 py-2 rounded-xl border text-xs font-semibold whitespace-nowrap shrink-0 transition-colors"
              :class="filterDate === todayStr ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
              @click="filterDate = (filterDate === todayStr ? '' : todayStr)"
            >
              Today
            </button>
            <button
              type="button"
              class="px-3 py-2 rounded-xl border text-xs font-semibold whitespace-nowrap shrink-0 transition-colors"
              :class="!filterDate ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
              @click="filterDate = ''"
            >
              All
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Filter Badges -->
    <div v-if="filterDoctorId || filterStatus || filterDate" class="mb-4 flex flex-wrap items-center gap-2 text-xs text-gray-600">
      <span class="font-medium">Active filters:</span>
      <span v-if="filterDate" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary-50 text-primary-700 border border-primary-200">
        <LucideCalendar class="h-3 w-3" />
        Date: {{ filterDate === todayStr ? 'Today' : filterDate }}
        <button class="hover:text-primary-900 ml-1 font-bold" @click="filterDate = ''">&times;</button>
      </span>
      <span v-if="filterDoctorId" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-300">
        Doctor: Dr. {{ doctorsStore.doctors.find(d => d.id === filterDoctorId)?.user.name || 'Selected' }}
        <button class="hover:text-gray-900 ml-1 font-bold" @click="filterDoctorId = ''">&times;</button>
      </span>
      <span v-if="filterStatus" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-300">
        Status: {{ filterStatus }}
        <button class="hover:text-gray-900 ml-1 font-bold" @click="filterStatus = ''">&times;</button>
      </span>
      <button class="text-primary-600 hover:underline font-medium text-xs ml-1" @click="filterDoctorId = ''; filterStatus = ''; filterDate = ''">
        Reset all filters
      </button>
    </div>

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

    <!-- Loading State -->
    <div v-if="appointmentsStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else-if="appointmentsStore.adminAppointments.length === 0"
      :title="filterDoctorId || filterStatus || filterDate ? 'No Appointments Match Filter' : 'No Appointments Found'"
      :description="filterDoctorId || filterStatus || filterDate ? 'No bookings found for the selected filter combination. Try clearing your filters.' : 'There are no patient appointments booked yet.'"
    >
      <template #icon>
        <LucideCalendarX class="h-10 w-10 text-gray-400" />
      </template>
      <template #actions>
        <button
          v-if="filterDoctorId || filterStatus || filterDate"
          class="btn-primary mt-4 text-xs"
          @click="filterDoctorId = ''; filterStatus = ''; filterDate = ''"
        >
          Show All Appointments
        </button>
      </template>
    </BaseEmptyState>

    <!-- Master Appointments Table -->
    <div v-else class="card-table">
      <table class="w-full text-left text-sm text-gray-700">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
          <tr>
            <th class="px-4 py-3">Reference / Patient</th>
            <th class="px-4 py-3">Doctor / Specialty</th>
            <th class="px-4 py-3">Scheduled Time</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="appt in appointmentsStore.adminAppointments" :key="appt.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <div class="font-mono text-xs text-gray-500 mb-0.5">{{ appt.appointment_reference }}</div>
              <div class="font-semibold text-gray-900">{{ appt.patient.user.name }}</div>
              <div class="text-xs text-gray-500">{{ appt.patient.user.email }}</div>
            </td>
            <td class="px-4 py-3">
              <div class="font-semibold text-gray-900">Dr. {{ appt.doctor.user.name }}</div>
              <div v-if="appt.doctor.specialty" class="text-xs text-teal-600 font-medium">{{ appt.doctor.specialty.name }}</div>
            </td>
            <td class="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">
              <div class="flex items-center gap-1.5">
                <span>{{ formatDate(appt.scheduled_at) }}</span>
                <span
                  v-if="appt.scheduled_at.startsWith(todayStr)"
                  class="px-1.5 py-0.5 text-[10px] font-bold rounded bg-green-100 text-green-700"
                >
                  Today
                </span>
              </div>
              <div class="font-mono text-xs text-gray-500">{{ formatTime(appt.scheduled_at) }}</div>
            </td>
            <td class="px-4 py-3">
              <BaseStatusBadge :status="appt.status" />
            </td>
            <td class="px-4 py-3 text-right whitespace-nowrap space-x-2">
              <button
                class="px-2 py-1 text-xs font-medium text-primary-700 hover:underline"
                @click="selectedPatientAppointment = appt"
              >Patient Info</button>
              <button
                v-if="appt.status === 'pending'"
                class="px-2 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700"
                @click="handleUpdateStatus(appt.id, 'confirmed')"
              >
                Confirm
              </button>
              <button
                v-if="appt.status !== 'cancelled' && appt.status !== 'completed'"
                class="px-2 py-1 border border-red-200 text-red-600 rounded text-xs font-medium hover:bg-red-50"
                @click="handleUpdateStatus(appt.id, 'cancelled')"
              >
                Cancel
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <FeaturesAppointmentsPatientInfoModal :model-value="Boolean(selectedPatientAppointment)" :appointment="selectedPatientAppointment" @update:model-value="!$event && (selectedPatientAppointment = null)" />
  </div>
</template>
