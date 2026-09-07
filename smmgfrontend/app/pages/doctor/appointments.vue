<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({
  middleware: 'auth',
})

const appointmentsStore = useAppointmentsStore()

const todayStr = new Date().toISOString().split('T')[0]
const selectedDate = ref<string>('')
const selectedStatus = ref<string>('')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)
const selectedPatientAppointment = ref<Appointment | null>(null)

onMounted(async () => {
  await appointmentsStore.fetchDoctorAppointments(selectedDate.value || undefined, selectedStatus.value || undefined)
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
      description="View full patient schedule and manage consultation status"
    >
      <template #actions>
        <div class="flex flex-col sm:flex-row items-end gap-3 w-full sm:w-auto text-left">
          <div class="w-full sm:w-auto">
            <div class="flex items-center justify-between mb-1">
              <label class="form-label mb-0 text-xs">Filter Date</label>
              <button
                v-if="selectedDate"
                type="button"
                class="text-[11px] font-semibold text-primary-600 hover:text-primary-800 hover:underline"
                @click="selectedDate = ''"
              >
                Clear (Show All)
              </button>
            </div>
            <div class="flex items-center gap-1.5">
              <input
                v-model="selectedDate"
                type="date"
                class="form-input w-full sm:w-44 text-xs"
              />
              <button
                type="button"
                class="px-2.5 py-1.5 rounded-lg border text-xs font-semibold whitespace-nowrap transition-colors"
                :class="selectedDate === todayStr ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
                @click="selectedDate = (selectedDate === todayStr ? '' : todayStr)"
              >
                Today
              </button>
              <button
                type="button"
                class="px-2.5 py-1.5 rounded-lg border text-xs font-semibold whitespace-nowrap transition-colors"
                :class="!selectedDate ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
                @click="selectedDate = ''"
              >
                All Dates
              </button>
            </div>
          </div>

          <div class="w-full sm:w-40">
            <label class="form-label mb-1 text-xs">Status</label>
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

    <!-- Active Filter Badges -->
    <div v-if="selectedDate || selectedStatus" class="mb-4 flex flex-wrap items-center gap-2 text-xs text-gray-600">
      <span class="font-medium">Active filters:</span>
      <span v-if="selectedDate" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary-50 text-primary-700 border border-primary-200">
        <LucideCalendar class="h-3 w-3" />
        Date: {{ selectedDate === todayStr ? 'Today' : selectedDate }}
        <button class="hover:text-primary-900 ml-1 font-bold" @click="selectedDate = ''">&times;</button>
      </span>
      <span v-if="selectedStatus" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-300">
        Status: {{ selectedStatus }}
        <button class="hover:text-gray-900 ml-1 font-bold" @click="selectedStatus = ''">&times;</button>
      </span>
      <button class="text-primary-600 hover:underline font-medium text-xs ml-1" @click="selectedDate = ''; selectedStatus = ''">
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
      v-else-if="appointmentsStore.doctorAppointments.length === 0"
      :title="selectedDate || selectedStatus ? 'No Consultations Match Filter' : 'No Consultations Scheduled'"
      :description="selectedDate || selectedStatus ? 'There are no appointments matching your selected filter. Try clearing the filter to view all bookings.' : 'You do not have any patient consultations booked yet.'"
    >
      <template #icon>
        <LucideCalendarX class="h-10 w-10 text-gray-400" />
      </template>
      <template #actions>
        <button
          v-if="selectedDate || selectedStatus"
          class="btn-primary mt-4 text-xs"
          @click="selectedDate = ''; selectedStatus = ''"
        >
          Show All Consultations
        </button>
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
            <td class="px-4 py-3 max-w-xs truncate">
              <div v-if="appt.service" class="font-medium text-gray-800">{{ appt.service.name }}</div>
              <div v-if="appt.reason" class="text-xs text-gray-500 truncate">{{ appt.reason }}</div>
            </td>
            <td class="px-4 py-3">
              <BaseStatusBadge :status="appt.status" />
            </td>
            <td class="px-4 py-3 text-right whitespace-nowrap space-x-2">
              <button class="px-2.5 py-1 text-xs font-medium text-primary-700 hover:underline" @click="selectedPatientAppointment = appt">Patient Info</button>
              <button
                v-if="appt.status === 'pending'"
                class="px-2.5 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700"
                @click="handleUpdateStatus(appt.id, 'confirmed')"
              >
                Confirm
              </button>
              <button
                v-if="appt.status === 'confirmed'"
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
    <FeaturesAppointmentsPatientInfoModal :model-value="Boolean(selectedPatientAppointment)" :appointment="selectedPatientAppointment" @update:model-value="!$event && (selectedPatientAppointment = null)" />
  </div>
</template>
