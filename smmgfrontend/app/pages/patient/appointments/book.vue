<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import { useDoctorsStore } from '~/stores/doctors'
import { useClinicServicesStore } from '~/stores/clinicServices'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const appointmentsStore = useAppointmentsStore()
const doctorsStore = useDoctorsStore()
const servicesStore = useClinicServicesStore()

const doctorId = String(route.query.doctor || '')
const date = String(route.query.date || '')
const time = String(route.query.time || '')
const serviceId = String(route.query.service || '')
const reason = ref('')
const loading = ref(true)
const saving = ref(false)
const errorMsg = ref<string | null>(null)
const bookedReference = ref<string | null>(null)
const bookedAppointmentId = ref<string | null>(null)

const serviceName = computed(() => servicesStore.services.find(item => item.id === serviceId)?.name || 'General Consultation')

onMounted(async () => {
  if (!doctorId || !date || !time) {
    errorMsg.value = 'Booking details are incomplete. Please select a doctor, date, and time again.'
    loading.value = false
    return
  }
  await Promise.all([doctorsStore.fetchDoctor(doctorId), servicesStore.fetchServices(true)])
  loading.value = false
})

const submitBooking = async () => {
  saving.value = true
  errorMsg.value = null
  try {
    const appointment = await appointmentsStore.createAppointment({
      doctor_profile_id: doctorId,
      service_id: serviceId || null,
      date,
      time,
      reason: reason.value || null,
    })
    bookedReference.value = appointment.appointment_reference
    bookedAppointmentId.value = appointment.id
    await router.push(`/patient/appointments/${appointment.id}`)
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to complete booking. Please select another time if this slot is no longer available.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-4 py-10 sm:px-6 space-y-6">
    <NuxtLink :to="doctorId ? `/doctors/${doctorId}` : '/doctors'" class="inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800">
      <LucideArrowLeft class="h-4 w-4" /> Back to doctor's schedule
    </NuxtLink>

    <!-- STEP-BY-STEP PROGRESS BAR (FROM CAPSTONE DOCX FLOW) -->
    <div class="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <p class="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-3">Booking Process: Step-by-Step</p>
      <div class="grid grid-cols-5 gap-1 sm:gap-2 text-center text-xs">
        <!-- Step 1: Book details -->
        <div class="flex flex-col items-center">
          <div class="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-primary-600 text-white font-bold text-xs shadow-sm ring-2 ring-primary-100">
            <LucideCheck class="h-4 w-4 stroke-[3]" />
          </div>
          <span class="mt-1 text-[10px] sm:text-[11px] font-semibold text-gray-900">1. Book Details</span>
        </div>

        <!-- Step 2: Dr. Schedule -->
        <div class="flex flex-col items-center">
          <div class="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-primary-600 text-white font-bold text-xs shadow-sm ring-2 ring-primary-100">
            <LucideCheck class="h-4 w-4 stroke-[3]" />
          </div>
          <span class="mt-1 text-[10px] sm:text-[11px] font-semibold text-gray-900">2. Dr. Schedule</span>
        </div>

        <!-- Step 3: Review info -->
        <div class="flex flex-col items-center">
          <div
            class="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full text-xs font-bold shadow-sm transition-all"
            :class="bookedReference ? 'bg-primary-600 text-white ring-2 ring-primary-100' : 'bg-amber-500 text-white ring-4 ring-amber-100'"
          >
            <LucideCheck v-if="bookedReference" class="h-4 w-4 stroke-[3]" />
            <span v-else>3</span>
          </div>
          <span class="mt-1 text-[10px] sm:text-[11px] font-bold" :class="bookedReference ? 'text-gray-900' : 'text-amber-700'">3. Review Info</span>
        </div>

        <!-- Step 4: Confirm booking -->
        <div class="flex flex-col items-center">
          <div
            class="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full text-xs font-bold shadow-sm transition-all"
            :class="bookedReference ? 'bg-primary-600 text-white ring-2 ring-primary-100' : 'border-2 border-gray-300 bg-white text-gray-400'"
          >
            <LucideCheck v-if="bookedReference" class="h-4 w-4 stroke-[3]" />
            <span v-else>4</span>
          </div>
          <span class="mt-1 text-[10px] sm:text-[11px] font-medium" :class="bookedReference ? 'text-gray-900 font-bold' : 'text-gray-400'">4. Confirm</span>
        </div>

        <!-- Step 5: Appointment details -->
        <div class="flex flex-col items-center">
          <div
            class="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full text-xs font-bold shadow-sm transition-all"
            :class="bookedReference ? 'bg-teal-600 text-white ring-4 ring-teal-100 animate-pulse' : 'border-2 border-gray-300 bg-white text-gray-400'"
          >
            <span>5</span>
          </div>
          <span class="mt-1 text-[10px] sm:text-[11px] font-medium" :class="bookedReference ? 'text-teal-800 font-bold' : 'text-gray-400'">5. Progress</span>
        </div>
      </div>
    </div>

    <section class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <header class="border-b border-gray-200 bg-gradient-to-r from-primary-50 via-white to-teal-50 px-6 py-6 sm:px-8">
        <p class="section-label">Step 3 & 4 of Booking Flow</p>
        <h1 class="mt-1 text-2xl font-bold text-slate-950">Review & Confirm Booking</h1>
        <p class="mt-2 text-sm text-slate-600">Review your chosen schedule, specify your visit symptoms, and submit for clinic approval.</p>
      </header>

      <div v-if="loading" class="flex justify-center py-20">
        <LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" />
      </div>

      <!-- SUCCESS CONFIRMATION & DIRECT LINK TO PROGRESS PAGE -->
      <div v-else-if="bookedReference" class="space-y-6 p-6 sm:p-8">
        <div class="rounded-xl border border-green-200 bg-green-50 p-5 text-green-900 space-y-3">
          <div class="flex items-center gap-3">
            <LucideCheckCircle2 class="h-7 w-7 text-green-600 shrink-0" />
            <div>
              <h2 class="text-base font-bold">Appointment Request Successfully Submitted!</h2>
              <p class="text-xs text-green-700 mt-0.5">Reference Number: <strong class="font-mono text-sm underline">{{ bookedReference }}</strong></p>
            </div>
          </div>
          <p class="text-xs text-green-800 leading-relaxed pt-2 border-t border-green-200/80">
            Your booking has entered the clinic queue in <strong>Pending</strong> status. <strong>Clinic Staff / Doctor's Assistant</strong> will review and confirm doctor availability. You will receive an email once confirmed.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row gap-3 pt-2">
          <NuxtLink
            v-if="bookedAppointmentId"
            :to="`/patient/appointments/${bookedAppointmentId}`"
            class="btn btn-primary flex-1 justify-center py-3 text-sm flex items-center gap-2"
          >
            <LucideActivity class="h-4 w-4" />
            <span>Track Live Booking Progress & Details &rarr;</span>
          </NuxtLink>
          <NuxtLink to="/patient/appointments" class="btn btn-secondary justify-center py-3 text-sm">
            View My Appointments
          </NuxtLink>
        </div>
      </div>

      <!-- REVIEW & CONFIRM FORM -->
      <form v-else class="space-y-6 p-6 sm:p-8" @submit.prevent="submitBooking">
        <BaseAlertBanner v-if="errorMsg" type="error" :message="errorMsg" @dismiss="errorMsg = null" />

        <div class="grid gap-4 rounded-xl border border-gray-200 bg-gray-50 p-5 sm:grid-cols-2">
          <div>
            <p class="text-xs font-medium text-gray-500">Doctor</p>
            <p class="mt-1 font-semibold text-gray-900">Dr. {{ doctorsStore.currentDoctor?.user.name || 'Unavailable' }}</p>
            <p v-if="doctorsStore.currentDoctor?.specialty" class="text-xs text-teal-700 mt-0.5 font-medium">{{ doctorsStore.currentDoctor.specialty.name }}</p>
          </div>
          <div>
            <p class="text-xs font-medium text-gray-500">Clinic Service</p>
            <p class="mt-1 font-semibold text-gray-900">{{ serviceName }}</p>
          </div>
          <div>
            <p class="text-xs font-medium text-gray-500">Date</p>
            <p class="mt-1 font-semibold text-gray-900">{{ date }}</p>
          </div>
          <div>
            <p class="text-xs font-medium text-gray-500">Time</p>
            <p class="mt-1 font-mono font-semibold text-gray-900">{{ time }}</p>
          </div>
        </div>

        <!-- Business Logic Info Callout -->
        <div class="rounded-xl border border-blue-100 bg-blue-50/70 p-4 text-xs text-blue-900 flex items-start gap-3">
          <LucideInfo class="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <p class="font-bold text-blue-950">Who approves this booking?</p>
            <p class="text-blue-800 leading-relaxed">
              Upon completing this booking, your appointment will be marked as <strong>Pending</strong>. Our <strong>Clinic Staff / Doctor's Assistant</strong> verifies the doctor's active schedule and approves the consultation. You will receive an automated confirmation email once approved.
            </p>
          </div>
        </div>

        <div>
          <label class="form-label">
            Reason for Visit / Symptoms <span class="font-normal text-gray-500">(optional)</span>
          </label>
          <textarea
            v-model="reason"
            rows="4"
            maxlength="1000"
            class="form-input"
            placeholder="Briefly describe your symptoms or reason for visit..."
          />
        </div>

        <div class="flex flex-col-reverse gap-3 border-t border-gray-200 pt-6 sm:flex-row sm:justify-end">
          <NuxtLink :to="`/doctors/${doctorId}`" class="btn btn-secondary justify-center">
            Cancel
          </NuxtLink>
          <button
            type="submit"
            class="btn btn-primary justify-center"
            :disabled="saving || !doctorsStore.currentDoctor"
          >
            <LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" />
            <LucideCalendarCheck v-else class="h-4 w-4" />
            <span>{{ saving ? 'Submitting Booking...' : 'Complete & Submit Booking' }}</span>
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
