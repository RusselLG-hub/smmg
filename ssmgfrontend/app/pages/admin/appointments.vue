<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import { useDoctorsStore } from '~/stores/doctors'

definePageMeta({
  middleware: 'auth',
})

const appointmentsStore = useAppointmentsStore()
const doctorsStore = useDoctorsStore()

const filterDoctorId = ref<string>('')
const filterStatus = ref<string>('')
const filterDate = ref<string>('')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

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
      title="Admin Appointments Management"
      description="Master appointment directory and clinic status controls"
    >
      <template #actions>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full text-left">
          <div>
            <label class="form-label mb-1">Doctor</label>
            <select v-model="filterDoctorId" class="form-input w-full text-xs">
              <option value="">All Doctors</option>
              <option v-for="d in doctorsStore.doctors" :key="d.id" :value="d.id">Dr. {{ d.user.name }}</option>
            </select>
          </div>

          <div>
            <label class="form-label mb-1">Status</label>
            <select v-model="filterStatus" class="form-input w-full text-xs">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div>
            <label class="form-label mb-1">Date</label>
            <input v-model="filterDate" type="date" class="form-input w-full text-xs" />
          </div>
        </div>
      </template>
    </BasePageHeader>

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
      title="No Appointments Found"
      description="There are no appointments matching your filter selection."
    >
      <template #icon>
        <LucideCalendarX class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <!-- Master Appointments Table -->
    <div v-else class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-x-auto">
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
              <div>{{ formatDate(appt.scheduled_at) }}</div>
              <div class="font-mono text-xs text-gray-500">{{ formatTime(appt.scheduled_at) }}</div>
            </td>
            <td class="px-4 py-3">
              <BaseStatusBadge :status="appt.status" />
            </td>
            <td class="px-4 py-3 text-right whitespace-nowrap space-x-2">
              <button
                v-if="appt.status === 'pending'"
                class="px-2 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700"
                @click="handleUpdateStatus(appt.id, 'confirmed')"
              >
                Confirm
              </button>
              <button
                v-if="appt.status === 'confirmed'"
                class="px-2 py-1 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700"
                @click="handleUpdateStatus(appt.id, 'completed')"
              >
                Mark Complete
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
  </div>
</template>
