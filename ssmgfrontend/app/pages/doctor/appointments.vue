<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({
  middleware: 'auth',
})

const appointmentsStore = useAppointmentsStore()

const todayStr = new Date().toISOString().split('T')[0]
const selectedDate = ref<string>(todayStr)
const selectedStatus = ref<string>('')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

onMounted(async () => {
  await appointmentsStore.fetchDoctorAppointments(selectedDate.value, selectedStatus.value || undefined)
})

watch([selectedDate, selectedStatus], async () => {
  await appointmentsStore.fetchDoctorAppointments(selectedDate.value || undefined, selectedStatus.value || undefined)
})

const handleUpdateStatus = async (id: string, newStatus: string) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await appointmentsStore.updateStatus(id, newStatus)
    actionSuccess.value = `Appointment status updated to ${newStatus}.`
    await appointmentsStore.fetchDoctorAppointments(selectedDate.value || undefined, selectedStatus.value || undefined)
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
      title="Doctor Consultations"
      description="View patient schedule and update consultation status"
    >
      <template #actions>
        <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto text-left">
          <div class="w-full sm:w-44">
            <label class="form-label mb-1">Filter Date</label>
            <input
              v-model="selectedDate"
              type="date"
              class="form-input w-full text-xs"
            />
          </div>

          <div class="w-full sm:w-40">
            <label class="form-label mb-1">Status</label>
            <select v-model="selectedStatus" class="form-input w-full text-xs">
              <option value="">All Statuses</option>
              <option value="confirmed">Confirmed</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
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
      v-else-if="appointmentsStore.doctorAppointments.length === 0"
      title="No Consultations Scheduled"
      description="There are no appointments matching your filter criteria."
    >
      <template #icon>
        <LucideCalendarX class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <!-- Appointment Table -->
    <div v-else class="card-table">
      <table class="w-full text-left text-sm text-gray-700">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
          <tr>
            <th class="px-4 py-3">Reference / Patient</th>
            <th class="px-4 py-3">Scheduled Time</th>
            <th class="px-4 py-3">Service / Reason</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="appt in appointmentsStore.doctorAppointments" :key="appt.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <div class="font-mono text-xs text-gray-500 mb-0.5">{{ appt.appointment_reference }}</div>
              <div class="font-semibold text-gray-900">{{ appt.patient.user.name }}</div>
              <div class="text-xs text-gray-500">{{ appt.patient.user.email }}</div>
            </td>
            <td class="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">
              <div>{{ formatDate(appt.scheduled_at) }}</div>
              <div class="font-mono text-xs text-gray-500">{{ formatTime(appt.scheduled_at) }}</div>
            </td>
            <td class="px-4 py-3 max-w-xs truncate">
              <div v-if="appt.service" class="font-medium text-gray-800">{{ appt.service.name }}</div>
              <div v-if="appt.reason" class="text-xs text-gray-500 truncate">{{ appt.reason }}</div>
            </td>
            <td class="px-4 py-3">
              <BaseStatusBadge :status="appt.status" />
            </td>
            <td class="px-4 py-3 text-right whitespace-nowrap space-x-2">
              <button
                v-if="appt.status === 'confirmed' || appt.status === 'pending'"
                class="px-2.5 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700"
                @click="handleUpdateStatus(appt.id, 'completed')"
              >
                Mark Completed
              </button>
              <button
                v-if="appt.status === 'confirmed' || appt.status === 'pending'"
                class="px-2.5 py-1 border border-red-200 text-red-600 rounded text-xs font-medium hover:bg-red-50"
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
