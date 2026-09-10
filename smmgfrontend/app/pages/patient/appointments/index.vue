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
  if (appt.status !== 'pending') return
  selectedAppointment.value = appt
  cancellationReason.value = ''
  actionError.value = null
  showCancelModal.value = true
}

const handleConfirmCancel = async () => {
  if (!selectedAppointment.value || selectedAppointment.value.status !== 'pending') return
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
  if (appt.status !== 'pending') return
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
    actionSuccess.value = `Appointment ${selectedAppointment.value.appointment_reference} rescheduled and submitted for clinic confirmation.`
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
    hour12: true,
  })
}
</script>

<template>
  <div class="page-container">
    <BasePageHeader
      kicker="Your Medical Calendar"
      title="My Appointments"
      description="Everything about your upcoming healthcare consultations and booking history, kept in one place."
    >
      <template #actions>
        <NuxtLink
          to="/book"
          class="btn-primary flex items-center gap-2"
        >
          <LucideCalendarPlus class="h-4 w-4" />
          <span>Book Consultation</span>
        </NuxtLink>
      </template>
    </BasePageHeader>

    <!-- Clinic Approval Business Logic Note -->
    <div class="mb-6 rounded-xl border border-blue-100 bg-blue-50/60 p-4 text-xs text-blue-900 flex items-start gap-3">
      <LucideInfo class="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
      <div class="space-y-0.5">
        <p class="font-semibold">How Appointment Approval Works:</p>
        <p class="text-blue-800 leading-relaxed">
          When you book, your consultation starts in <strong>Pending</strong> status. Our <strong>Clinic Staff / Doctor's Assistant</strong> verifies the doctor's schedule and room availability, then confirms your booking. You can click on any appointment below to view its live step-by-step progress.
        </p>
      </div>
    </div>

    <!-- Alert Notifications -->
    <div v-if="actionSuccess" class="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideCheckCircle2 class="h-5 w-5 text-green-500" />
        <span>{{ actionSuccess }}</span>
      </div>
      <button class="text-green-700 font-bold text-base" @click="actionSuccess = null">&times;</button>
    </div>

    <div v-if="actionError" class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideAlertCircle class="h-5 w-5 text-red-500" />
        <span>{{ actionError }}</span>
      </div>
      <button class="text-red-700 font-bold text-base" @click="actionError = null">&times;</button>
    </div>

    <!-- Navigation Tab Pills (Distinct Indigo Theme) -->
    <div class="mb-6 inline-flex rounded-xl border border-indigo-100 bg-white p-1 shadow-xs">
      <button
        type="button"
        class="rounded-lg px-4 py-2 text-xs sm:text-sm font-semibold transition-all flex items-center gap-1.5"
        :class="activeTab === 'upcoming' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
        @click="handleTabChange('upcoming')"
      >
        <LucideCalendarCheck class="h-4 w-4" />
        <span>Upcoming Consultations</span>
      </button>

      <button
        type="button"
        class="rounded-lg px-4 py-2 text-xs sm:text-sm font-semibold transition-all flex items-center gap-1.5"
        :class="activeTab === 'past' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
        @click="handleTabChange('past')"
      >
        <LucideHistory class="h-4 w-4" />
        <span>Past & Cancelled</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="appointmentsStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-indigo-600 animate-spin" />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="appointmentsStore.myAppointments.length === 0"
      class="rounded-2xl border border-dashed border-indigo-200 bg-white p-12 text-center shadow-xs"
    >
      <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-700 mb-4">
        <LucideCalendar class="h-6 w-6" />
      </div>
      <h3 class="text-lg font-bold text-gray-900">No appointments found</h3>
      <p class="mt-1 text-sm text-gray-500">You have no {{ activeTab }} consultations recorded.</p>
      <NuxtLink v-if="activeTab === 'upcoming'" to="/book" class="btn bg-emerald-600 text-white hover:bg-emerald-700 px-6 py-2.5 mt-5 inline-flex items-center gap-2 shadow-sm hover:shadow-md transition-all">
        <LucideCalendarPlus class="h-4 w-4" />
        <span>Book your consultation</span>
      </NuxtLink>
    </div>

    <!-- Improved Appointments Cards Grid (Distinct Indigo/Slate Theme) -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <article
        v-for="appt in appointmentsStore.myAppointments"
        :key="appt.id"
        class="group flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xs transition-all duration-200 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-md"
      >
        <!-- Top header strip with Reference & Status badge -->
        <div class="flex items-center justify-between border-b border-indigo-50 bg-gradient-to-r from-indigo-50/70 via-white to-indigo-50/30 px-5 py-3.5">
          <span class="font-mono text-xs font-bold text-gray-700 bg-white px-2.5 py-1 rounded-lg border border-gray-200 shadow-2xs">
            {{ appt.appointment_reference }}
          </span>
          <BaseStatusBadge :status="appt.status" />
        </div>

        <!-- Card Body -->
        <div class="flex flex-1 flex-col p-5 space-y-4">
          <!-- Doctor Header with Avatar -->
          <div class="flex items-start gap-3.5">
            <div class="h-12 w-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-base shrink-0 overflow-hidden shadow-2xs">
              <img
                v-if="appt.doctor.profile_image_url"
                :src="appt.doctor.profile_image_url"
                :alt="appt.doctor.user.name"
                class="h-full w-full object-cover"
              />
              <LucideStethoscope v-else class="h-6 w-6 text-indigo-600" />
            </div>

            <div class="min-w-0 flex-1">
              <h3 class="font-bold text-base text-gray-900 leading-snug truncate">
                Dr. {{ appt.doctor.user.name }}
              </h3>
              <p class="text-xs font-semibold text-indigo-700 flex items-center gap-1 mt-0.5">
                <LucideActivity class="h-3 w-3" />
                <span>{{ appt.doctor.specialty?.name || 'Medical Specialist' }}</span>
              </p>
              <p v-if="appt.service" class="text-[11px] text-gray-500 truncate mt-0.5">
                Service: <strong class="text-gray-700 font-medium">{{ appt.service.name }}</strong>
              </p>
            </div>
          </div>

          <!-- Schedule Date & Time Box -->
          <div class="bg-gray-50/90 rounded-xl p-3.5 border border-gray-100 space-y-2 text-xs font-medium text-gray-800">
            <div class="flex items-center gap-2">
              <LucideCalendar class="h-4 w-4 text-primary-600 shrink-0" />
              <span>{{ formatDate(appt.scheduled_at) }}</span>
            </div>
            <div class="flex items-center gap-2 font-mono">
              <LucideClock class="h-4 w-4 text-primary-600 shrink-0" />
              <span>{{ formatTime(appt.scheduled_at) }}</span>
            </div>
          </div>

          <!-- Reason / Symptoms snippet -->
          <div v-if="appt.reason" class="text-xs text-gray-600 bg-white p-2.5 rounded-lg border border-gray-100 line-clamp-2">
            <span class="font-semibold text-gray-700">Symptoms:</span> {{ appt.reason }}
          </div>

          <!-- Cancellation note if present -->
          <div v-if="appt.cancellation_reason" class="text-xs text-red-700 bg-red-50 p-2.5 rounded-lg border border-red-100">
            <span class="font-semibold">Cancellation Note:</span> {{ appt.cancellation_reason }}
          </div>

          <!-- Compact Stepper Progress Tracker -->
          <div class="pt-2 pb-1 border-t border-gray-100">
            <FeaturesAppointmentsBookingProgressTracker
              :appointment="appt"
              :compact="true"
              :show-logic-details="false"
            />
          </div>

          <!-- Card Actions at Bottom -->
          <div class="mt-auto pt-3 border-t border-gray-100 space-y-2">
            <NuxtLink
              :to="`/patient/appointments/${appt.id}`"
              class="flex w-full items-center justify-between rounded-xl bg-indigo-50/80 border border-indigo-200/70 px-4 py-2.5 text-xs font-bold text-indigo-900 transition-colors group-hover:bg-indigo-100 hover:text-indigo-950"
            >
              <span>View details & live tracker</span>
              <LucideArrowRight class="h-4 w-4" />
            </NuxtLink>

            <!-- Actions: Reschedule / Cancel only for Pending consultations -->
            <div v-if="appt.status === 'pending'" class="flex gap-2">
              <button
                type="button"
                class="flex-1 py-1.5 px-3 rounded-lg border border-gray-200 bg-white text-xs font-medium text-gray-700 hover:bg-gray-50 text-center transition-colors"
                @click="openRescheduleModal(appt)"
              >
                Reschedule
              </button>
              <button
                type="button"
                class="py-1.5 px-3 rounded-lg border border-red-200 bg-red-50 text-xs font-medium text-red-700 hover:bg-red-100 transition-colors"
                @click="openCancelModal(appt)"
              >
                Cancel
              </button>
            </div>

            <!-- Confirmed: Patient cannot cancel or reschedule online -->
            <div
              v-else-if="appt.status === 'confirmed'"
              class="flex items-center gap-1.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80 px-3 py-2 text-[11px] text-emerald-800"
            >
              <LucideLock class="h-3.5 w-3.5 text-emerald-600 shrink-0" />
              <span>Confirmed booking · Contact clinic to modify</span>
            </div>
          </div>
        </div>
      </article>
    </div>

    <!-- CANCEL APPOINTMENT MODAL -->
    <div v-if="showCancelModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Cancel appointment" @click.self="showCancelModal = false">
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
    <div v-if="showRescheduleModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Reschedule appointment" @click.self="showRescheduleModal = false">
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
