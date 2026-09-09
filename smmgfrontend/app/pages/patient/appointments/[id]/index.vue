<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const appointmentsStore = useAppointmentsStore()

const appointmentId = String(route.params.id)
const appointment = ref<Appointment | null>(null)
const loading = ref(true)
const errorMessage = ref<string | null>(null)
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

// Cancel Modal State
const showCancelModal = ref(false)
const cancellationReason = ref('')
const isCancelling = ref(false)

const loadAppointment = async () => {
  loading.value = true
  errorMessage.value = null
  try {
    const data = await appointmentsStore.fetchAppointmentDetails(appointmentId)
    appointment.value = data
  } catch (err: any) {
    errorMessage.value = err?.data?.detail || 'Failed to load appointment details.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadAppointment()
})

const formatDate = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
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

// Can cancel or reschedule only if status is pending, and more than 24h away
const canModify = computed(() => {
  if (!appointment.value) return false
  if (appointment.value.status !== 'pending') return false
  const scheduledTime = new Date(appointment.value.scheduled_at).getTime()
  const now = Date.now()
  const hoursUntil = (scheduledTime - now) / (1000 * 60 * 60)
  return hoursUntil >= 24
})

const handleConfirmCancel = async () => {
  if (!appointment.value || appointment.value.status !== 'pending') return
  isCancelling.value = true
  actionError.value = null
  actionSuccess.value = null

  try {
    const updated = await appointmentsStore.cancelAppointment(
      appointment.value.id,
      cancellationReason.value || undefined,
    )
    appointment.value = updated
    actionSuccess.value = `Appointment ${appointment.value.appointment_reference} has been cancelled.`
    showCancelModal.value = false
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to cancel appointment.'
  } finally {
    isCancelling.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">
    <!-- Top Back Navigation -->
    <div class="flex items-center justify-between">
      <NuxtLink
        to="/patient/appointments"
        class="inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800 transition-colors"
      >
        <LucideArrowLeft class="h-4 w-4" />
        <span>Back to My Appointments</span>
      </NuxtLink>

      <NuxtLink
        to="/doctors"
        class="btn btn-secondary !py-1.5 !px-3 text-xs hidden sm:inline-flex items-center gap-1.5"
      >
        <LucidePlus class="h-3.5 w-3.5" />
        <span>Book Another Consultation</span>
      </NuxtLink>
    </div>

    <!-- Alert Notifications -->
    <div
      v-if="actionSuccess"
      class="rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-800 flex items-center justify-between"
    >
      <div class="flex items-center gap-2">
        <LucideCheckCircle2 class="h-5 w-5 text-green-600 shrink-0" />
        <span>{{ actionSuccess }}</span>
      </div>
      <button class="font-bold text-green-700 hover:text-green-900" @click="actionSuccess = null">&times;</button>
    </div>

    <div
      v-if="actionError"
      class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 flex items-center justify-between"
    >
      <div class="flex items-center gap-2">
        <LucideAlertCircle class="h-5 w-5 text-red-600 shrink-0" />
        <span>{{ actionError }}</span>
      </div>
      <button class="font-bold text-red-700 hover:text-red-900" @click="actionError = null">&times;</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-24">
      <LucideLoader2 class="h-10 w-10 animate-spin text-primary-600" />
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage || !appointment" class="rounded-2xl border border-gray-200 bg-white p-12 text-center shadow-sm">
      <LucideAlertCircle class="mx-auto h-12 w-12 text-red-500 mb-3" />
      <h2 class="text-xl font-bold text-gray-900">Appointment Not Found</h2>
      <p class="mt-2 text-sm text-gray-600">{{ errorMessage || 'We could not locate this appointment record.' }}</p>
      <NuxtLink to="/patient/appointments" class="btn btn-primary mt-6">
        View All Appointments
      </NuxtLink>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-8">
      <!-- Top Overview Header -->
      <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <span class="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-wider text-teal-700">
              Healthcare Consultation
            </span>
            <h1 class="mt-1 text-2xl font-extrabold text-slate-950 sm:text-3xl">
              Appointment Details & Progress
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Booked on {{ formatDate(appointment.created_at) }}
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <span class="rounded-lg border border-gray-200 bg-gray-50 px-3.5 py-1.5 font-mono text-sm font-bold text-gray-800">
              {{ appointment.appointment_reference }}
            </span>
            <BaseStatusBadge :status="appointment.status" />
          </div>
        </div>
      </div>

      <!-- Service / Booking Progress Tracker (Requested by User) -->
      <FeaturesAppointmentsBookingProgressTracker
        :appointment="appointment"
        :show-logic-details="true"
      />

      <!-- Appointment Information Grid -->
      <div class="grid gap-6 md:grid-cols-2">
        <!-- Assigned Doctor Card -->
        <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-gray-100 pb-3">
            <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
              <LucideStethoscope class="h-4 w-4 text-primary-600" />
              <span>Assigned Healthcare Provider</span>
            </h3>
            <NuxtLink
              :to="`/doctors/${appointment.doctor_profile_id}`"
              class="text-xs font-semibold text-primary-600 hover:underline"
            >
              View Profile &rarr;
            </NuxtLink>
          </div>

          <div class="flex items-start gap-4">
            <div class="h-16 w-16 rounded-full overflow-hidden bg-primary-50 border-2 border-primary-200 shrink-0 flex items-center justify-center">
              <BaseAvatar
                :src="appointment.doctor.profile_image_url"
                :alt="`Dr. ${appointment.doctor.user.name}`"
                fallback="/images/public-doctor-fallback.svg"
              />
            </div>

            <div class="space-y-1 text-xs">
              <h4 class="text-base font-bold text-gray-900">
                Dr. {{ appointment.doctor.user.name }}
              </h4>
              <p v-if="appointment.doctor.specialty" class="text-teal-700 font-semibold flex items-center gap-1">
                <LucideActivity class="h-3 w-3" />
                {{ appointment.doctor.specialty.name }}
              </p>
              <p v-if="appointment.doctor.title" class="text-gray-500">
                {{ appointment.doctor.title }}
              </p>
              <p class="text-gray-500 flex items-center gap-1 pt-1">
                <LucideMail class="h-3 w-3 text-gray-400" />
                {{ appointment.doctor.user.email }}
              </p>
            </div>
          </div>
        </div>

        <!-- Schedule & Location Card -->
        <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm space-y-4">
          <div class="border-b border-gray-100 pb-3">
            <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
              <LucideCalendarClock class="h-4 w-4 text-primary-600" />
              <span>Schedule & Consultation Time</span>
            </h3>
          </div>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <div class="rounded-xl border border-gray-100 bg-gray-50 p-3.5">
              <span class="font-medium text-gray-500">Scheduled Date</span>
              <p class="mt-1 text-sm font-bold text-gray-900">
                {{ formatDate(appointment.scheduled_at) }}
              </p>
            </div>

            <div class="rounded-xl border border-gray-100 bg-gray-50 p-3.5">
              <span class="font-medium text-gray-500">Scheduled Time</span>
              <p class="mt-1 font-mono text-sm font-bold text-gray-900">
                {{ formatTime(appointment.scheduled_at) }}
              </p>
            </div>

            <div class="rounded-xl border border-gray-100 bg-gray-50 p-3.5">
              <span class="font-medium text-gray-500">Clinic Service</span>
              <p class="mt-1 font-semibold text-gray-900">
                {{ appointment.service?.name || 'General Consultation' }}
              </p>
            </div>

            <div class="rounded-xl border border-gray-100 bg-gray-50 p-3.5">
              <span class="font-medium text-gray-500">Email Reminder</span>
              <p class="mt-1 font-semibold" :class="appointment.reminder_sent_at ? 'text-teal-700' : 'text-gray-600'">
                {{ appointment.reminder_sent_at ? 'Sent' : 'Scheduled' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Visit Reason / Symptoms Card -->
      <div v-if="appointment.reason" class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm space-y-2">
        <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
          <LucideClipboardList class="h-4 w-4 text-primary-600" />
          <span>Patient Reason for Visit / Symptoms</span>
        </h3>
        <p class="text-xs text-gray-700 bg-gray-50 p-4 rounded-xl border border-gray-100 leading-relaxed whitespace-pre-line">
          {{ appointment.reason }}
        </p>
      </div>

      <!-- Action Buttons Footer -->
      <div class="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-4 border-t border-gray-200 pt-6">
        <NuxtLink to="/patient/appointments" class="btn btn-secondary justify-center">
          <LucideArrowLeft class="h-4 w-4" />
          <span>Back to All Appointments</span>
        </NuxtLink>

        <!-- Pending: Patient can reschedule or cancel (subject to 24h rule) -->
        <div v-if="appointment.status === 'pending'" class="flex flex-wrap gap-3 justify-end items-center">
          <NuxtLink
            v-if="canModify"
            :to="`/patient/appointments/${appointment.id}/reschedule`"
            class="btn btn-secondary !border-primary-300 text-primary-700 hover:bg-primary-50 justify-center"
          >
            <LucideRefreshCw class="h-4 w-4" />
            <span>Reschedule</span>
          </NuxtLink>

          <button
            v-if="canModify"
            type="button"
            class="btn !bg-red-50 !text-red-700 !border-red-200 hover:!bg-red-100 justify-center"
            @click="showCancelModal = true"
          >
            <LucideXCircle class="h-4 w-4" />
            <span>Cancel Appointment</span>
          </button>

          <span v-else class="text-xs text-gray-500 italic flex items-center">
            * Changes are restricted within 24 hours of consultation time.
          </span>
        </div>

        <!-- Confirmed: Locked for patient modification -->
        <div
          v-else-if="appointment.status === 'confirmed'"
          class="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2.5 text-xs text-emerald-800"
        >
          <LucideCheckCircle2 class="h-4 w-4 text-emerald-600 shrink-0" />
          <span>This appointment is confirmed. To cancel or change your schedule, please contact clinic staff directly.</span>
        </div>
      </div>
    </div>

    <!-- CANCEL APPOINTMENT MODAL -->
    <div
      v-if="showCancelModal"
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Cancel appointment"
      @click.self="showCancelModal = false"
    >
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Cancel Appointment</h3>
        <p class="text-xs text-gray-600">
          Appointments cannot be cancelled by patients within 24 hours of scheduled time. Are you sure you want to cancel reference <strong class="font-mono text-gray-900">{{ appointment?.appointment_reference }}</strong>?
        </p>

        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">
            Cancellation Reason (Optional)
          </label>
          <textarea
            v-model="cancellationReason"
            rows="3"
            placeholder="Reason for cancellation..."
            class="form-input w-full"
          />
        </div>

        <div class="modal-actions">
          <button
            type="button"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            @click="showCancelModal = false"
          >
            Keep Appointment
          </button>
          <button
            type="button"
            :disabled="isCancelling"
            class="btn !bg-red-600 !text-white hover:!bg-red-700 flex items-center gap-2 text-sm"
            @click="handleConfirmCancel"
          >
            <LucideLoader2 v-if="isCancelling" class="h-4 w-4 animate-spin" />
            <span>Confirm Cancel</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
