<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import { useSchedulesStore } from '~/stores/schedules'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({
  middleware: 'auth',
})

const appointmentsStore = useAppointmentsStore()
const schedulesStore = useSchedulesStore()

const activeTab = ref<'upcoming' | 'past'>('upcoming')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

// Cancel Modal State
const showCancelModal = ref(false)
const selectedAppointment = ref<Appointment | null>(null)
const cancellationReason = ref('')
const isCancelling = ref(false)

// Reschedule Modal State
const showRescheduleModal = ref(false)
const rescheduleDate = ref('')
const rescheduleSlot = ref<string | null>(null)
const isRescheduling = ref(false)

onMounted(async () => {
  await appointmentsStore.fetchMyAppointments(activeTab.value)
})

const handleTabChange = async (tab: 'upcoming' | 'past') => {
  activeTab.value = tab
  await appointmentsStore.fetchMyAppointments(tab)
}

const openCancelModal = (appt: Appointment) => {
  selectedAppointment.value = appt
  cancellationReason.value = ''
  actionError.value = null
  showCancelModal.value = true
}

const handleConfirmCancel = async () => {
  if (!selectedAppointment.value) return
  isCancelling.value = true
  actionError.value = null
  actionSuccess.value = null

  try {
    await appointmentsStore.cancelAppointment(
      selectedAppointment.value.id,
      cancellationReason.value || undefined
    )
    actionSuccess.value = `Appointment ${selectedAppointment.value.appointment_reference} has been cancelled.`
    showCancelModal.value = false
    await appointmentsStore.fetchMyAppointments(activeTab.value)
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to cancel appointment.'
  } finally {
    isCancelling.value = false
  }
}

const openRescheduleModal = async (appt: Appointment) => {
  selectedAppointment.value = appt
  const dateOnly = appt.scheduled_at.split('T')[0]
  rescheduleDate.value = dateOnly
  rescheduleSlot.value = null
  actionError.value = null
  showRescheduleModal.value = true
  await schedulesStore.fetchAvailability(appt.doctor_profile_id, dateOnly)
}

const handleRescheduleDateChange = async () => {
  if (selectedAppointment.value && rescheduleDate.value) {
    rescheduleSlot.value = null
    await schedulesStore.fetchAvailability(selectedAppointment.value.doctor_profile_id, rescheduleDate.value)
  }
}

const handleConfirmReschedule = async () => {
  if (!selectedAppointment.value || !rescheduleSlot.value) return
  isRescheduling.value = true
  actionError.value = null
  actionSuccess.value = null

  try {
    await appointmentsStore.rescheduleAppointment(
      selectedAppointment.value.id,
      rescheduleDate.value,
      rescheduleSlot.value
    )
    actionSuccess.value = `Appointment ${selectedAppointment.value.appointment_reference} rescheduled successfully.`
    showRescheduleModal.value = false
    await appointmentsStore.fetchMyAppointments(activeTab.value)
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to reschedule appointment.'
  } finally {
    isRescheduling.value = false
  }
}

const formatDate = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
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
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <BasePageHeader
      title="My Appointments"
      description="Manage your healthcare consultations and booking history"
    >
      <template #actions>
        <NuxtLink to="/doctors" class="btn btn-primary">
          <LucidePlus class="h-4 w-4" />
          <span>Book New Appointment</span>
        </NuxtLink>
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

    <!-- Navigation Tabs -->
    <div class="border-b border-gray-200 mb-6 flex gap-4">
      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'upcoming' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="handleTabChange('upcoming')"
      >
        <LucideCalendarCheck class="h-4 w-4" />
        <span>Upcoming Appointments</span>
      </button>

      <button
        class="py-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2"
        :class="activeTab === 'past' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
        @click="handleTabChange('past')"
      >
        <LucideHistory class="h-4 w-4" />
        <span>History & Cancelled</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="appointmentsStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else-if="appointmentsStore.myAppointments.length === 0"
      title="No Appointments Found"
      :description="`You have no ${activeTab} appointments recorded.`"
    >
      <template #icon>
        <LucideCalendarX class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <!-- Appointments Cards / Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="appt in appointmentsStore.myAppointments"
        :key="appt.id"
        class="card card-hover space-y-4"
      >
        <div class="flex items-center justify-between pb-3 border-b border-gray-100">
          <span class="font-mono text-xs font-bold text-gray-700 bg-gray-100 px-2.5 py-1 rounded border">
            {{ appt.appointment_reference }}
          </span>

          <!-- Status Badge -->
          <BaseStatusBadge :status="appt.status" />
        </div>

        <div class="space-y-2 text-sm">
          <div class="font-bold text-gray-900 text-base">
            Dr. {{ appt.doctor.user.name }}
          </div>

          <div v-if="appt.doctor.specialty" class="text-teal-600 text-xs font-semibold flex items-center gap-1">
            <LucideActivity class="h-3.5 w-3.5" />
            <span>{{ appt.doctor.specialty.name }}</span>
          </div>

          <div v-if="appt.service" class="text-gray-600 text-xs">
            Service: <strong class="text-gray-800">{{ appt.service.name }}</strong>
          </div>

          <div class="bg-gray-50 p-3 rounded-lg border border-gray-200 flex items-center justify-between text-xs font-medium">
            <div class="flex items-center gap-1.5 text-gray-700">
              <LucideCalendar class="h-4 w-4 text-gray-400" />
              <span>{{ formatDate(appt.scheduled_at) }}</span>
            </div>
            <div class="flex items-center gap-1.5 font-mono text-gray-900">
              <LucideClock class="h-4 w-4 text-gray-400" />
              <span>{{ formatTime(appt.scheduled_at) }}</span>
            </div>
          </div>

          <div v-if="appt.reason" class="text-xs text-gray-600 bg-gray-50/50 p-2.5 rounded border border-gray-100">
            <span class="font-semibold text-gray-700">Reason:</span> {{ appt.reason }}
          </div>

          <div v-if="appt.cancellation_reason" class="text-xs text-red-600 bg-red-50 p-2.5 rounded border border-red-100">
            <span class="font-semibold">Cancellation Note:</span> {{ appt.cancellation_reason }}
          </div>
        </div>

        <!-- Action Buttons for Upcoming Active Appointments -->
        <div v-if="appt.status === 'confirmed' || appt.status === 'pending'" class="pt-3 border-t border-gray-100 flex gap-3">
          <button
            type="button"
            class="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 hover:bg-gray-50"
            @click="openRescheduleModal(appt)"
          >
            Reschedule
          </button>
          <button
            type="button"
            class="px-3 py-1.5 border border-red-200 bg-red-50 rounded-lg text-xs font-medium text-red-700 hover:bg-red-100"
            @click="openCancelModal(appt)"
          >
            Cancel Appointment
          </button>
        </div>
      </div>
    </div>

    <!-- CANCEL APPOINTMENT MODAL -->
    <div v-if="showCancelModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Cancel appointment">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Cancel Appointment</h3>
        <p class="text-xs text-gray-600">
          Appointments cannot be cancelled within 24 hours of scheduled time.
        </p>

        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Cancellation Reason (Optional)</label>
          <textarea v-model="cancellationReason" rows="3" placeholder="Reason for cancellation..." class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showCancelModal = false">Keep Appointment</button>
          <button
            type="button"
            :disabled="isCancelling"
            class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 flex items-center gap-2"
            @click="handleConfirmCancel"
          >
            <LucideLoader2 v-if="isCancelling" class="h-4 w-4 animate-spin" />
            <span>Confirm Cancel</span>
          </button>
        </div>
      </div>
    </div>

    <!-- RESCHEDULE APPOINTMENT MODAL -->
    <div v-if="showRescheduleModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Reschedule appointment">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Reschedule Appointment</h3>

        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">New Date</label>
          <input
            v-model="rescheduleDate"
            type="date"
            class="w-full px-3 py-2 border rounded-lg text-sm"
            @change="handleRescheduleDateChange"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Select Available Time Slot</label>
          <div v-if="schedulesStore.loading" class="py-4 text-center">
            <LucideLoader2 class="h-5 w-5 text-primary-600 animate-spin mx-auto" />
          </div>

          <div v-else-if="!schedulesStore.availability || schedulesStore.availability.slots.length === 0" class="p-4 bg-gray-50 rounded text-center text-xs text-gray-500">
            No slots available on selected date.
          </div>

          <div v-else class="grid max-h-48 grid-cols-1 gap-2 overflow-y-auto min-[380px]:grid-cols-2">
            <button
              v-for="slot in schedulesStore.availability.slots"
              :key="slot.start_time"
              type="button"
              class="px-2.5 py-1.5 border rounded text-xs font-mono"
              :class="rescheduleSlot === slot.start_time ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-800 hover:bg-gray-50'"
              @click="rescheduleSlot = slot.start_time"
            >
              {{ slot.start_time }} &mdash; {{ slot.end_time }}
            </button>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showRescheduleModal = false">Cancel</button>
          <button
            type="button"
            :disabled="isRescheduling || !rescheduleSlot"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center gap-2"
            @click="handleConfirmReschedule"
          >
            <LucideLoader2 v-if="isRescheduling" class="h-4 w-4 animate-spin" />
            <span>Confirm Reschedule</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
