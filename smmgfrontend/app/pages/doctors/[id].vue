<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useDoctorsStore } from '~/stores/doctors'
import { useSchedulesStore } from '~/stores/schedules'
import { useClinicServicesStore } from '~/stores/clinicServices'
import { useAppointmentsStore } from '~/stores/appointments'
import { useAuthStore } from '~/stores/auth'
import type { Appointment } from '~~/shared/types/Appointment'

const route = useRoute()
const router = useRouter()
const doctorsStore = useDoctorsStore()
const schedulesStore = useSchedulesStore()
const clinicServicesStore = useClinicServicesStore()
const appointmentsStore = useAppointmentsStore()
const authStore = useAuthStore()

const doctorId = String(route.params.id)
const todayStr = new Date().toISOString().split('T')[0]

const selectedDate = ref(todayStr)
const monthCursor = ref(new Date(`${todayStr}T00:00:00`))
const selectedSlot = ref<string | null>(null)
const selectedServiceId = ref<string>(String(route.query.service || ''))
const reasonInput = ref('')

const createdAppointment = ref<Appointment | null>(null)
const showBookingModal = ref(false)
const bookingSuccess = ref<{ reference: string; date: string; time: string } | null>(null)
const bookingError = ref<string | null>(null)
const isSubmitting = ref(false)

const selectedServiceName = computed(() => {
  if (!selectedServiceId.value) return 'General Consultation'
  return clinicServicesStore.services.find(s => s.id === selectedServiceId.value)?.name || 'General Consultation'
})

const formatLongDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(`${dateStr}T00:00:00`)
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const handleOpenBookingModal = () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  if (!selectedSlot.value) return
  showBookingModal.value = true
}
const calendarWeekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const monthLabel = computed(() => monthCursor.value.toLocaleDateString(undefined, { month: 'long', year: 'numeric' }))
const compatibleServices = computed(() => {
  const specialtyId = doctorsStore.currentDoctor?.specialty_id
  return clinicServicesStore.services.filter(service =>
    !service.specialty_id || service.specialty_id === specialtyId,
  )
})
const calendarDays = computed(() => {
  const response = schedulesStore.monthlyAvailability
  if (!response) return []
  const leading = new Date(response.year, response.month - 1, 1).getDay()
  return [
    ...Array.from({ length: leading }, () => null),
    ...response.days,
  ]
})

const loadMonth = async () => {
  await schedulesStore.fetchMonthlyAvailability(
    doctorId,
    monthCursor.value.getFullYear(),
    monthCursor.value.getMonth() + 1,
  )
}

const changeMonth = async (offset: number) => {
  const next = new Date(monthCursor.value)
  next.setMonth(next.getMonth() + offset, 1)
  monthCursor.value = next
  selectedSlot.value = null
  schedulesStore.availability = null
  await loadMonth()
}

const selectAvailabilityDay = (date: string) => {
  if (date < todayStr) return
  const day = schedulesStore.monthlyAvailability?.days.find(item => item.date === date)
  selectedDate.value = date
  selectedSlot.value = null
  schedulesStore.availability = day || null
}

onMounted(async () => {
  await Promise.all([
    doctorsStore.fetchDoctor(doctorId),
    clinicServicesStore.fetchServices(true),
  ])
  if (doctorsStore.currentDoctor) {
    if (selectedServiceId.value && !compatibleServices.value.some(service => service.id === selectedServiceId.value)) {
      selectedServiceId.value = ''
    }
    await loadMonth()
    selectAvailabilityDay(selectedDate.value)
  }
})

const handleInitiateBooking = () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  if (!selectedSlot.value) return
  router.push({
    path: '/book',
    query: {
      doctor: doctorId,
      date: selectedDate.value,
      time: selectedSlot.value,
      ...(selectedServiceId.value ? { service: selectedServiceId.value } : {}),
    },
  })
}

const handleConfirmBooking = async () => {
  if (!selectedSlot.value) return
  isSubmitting.value = true
  bookingError.value = null

  try {
    const res = await appointmentsStore.createAppointment({
      doctor_profile_id: doctorId,
      service_id: selectedServiceId.value || null,
      date: selectedDate.value,
      time: selectedSlot.value,
      reason: reasonInput.value || null,
    })

    createdAppointment.value = res
    bookingSuccess.value = {
      reference: res.appointment_reference,
      date: selectedDate.value,
      time: selectedSlot.value,
    }
    showBookingModal.value = false
    selectedSlot.value = null
    reasonInput.value = ''

    // Refresh availability slots after booking
    await schedulesStore.fetchAvailability(doctorId, selectedDate.value)
    await loadMonth()
  } catch (err: any) {
    bookingError.value = err?.data?.detail || 'Failed to complete booking. Please try another time slot.'
    // Refresh availability in case of conflict
    await schedulesStore.fetchAvailability(doctorId, selectedDate.value)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-10 space-y-8">
    <NuxtLink to="/doctors" class="inline-flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-primary-600">
      <LucideArrowLeft class="h-4 w-4" />
      <span>Back to Doctors Directory</span>
    </NuxtLink>

    <div v-if="doctorsStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <div v-else-if="!doctorsStore.currentDoctor" class="bg-white rounded-xl border border-gray-200 p-12 text-center">
      <LucideAlertCircle class="h-12 w-12 text-red-500 mx-auto mb-3" />
      <h3 class="text-lg font-semibold text-gray-900">Doctor Profile Not Found</h3>
    </div>

    <div v-else class="space-y-8">
      <!-- Success Banner with Live Progress Tracker -->
      <div v-if="createdAppointment" class="space-y-4">
        <FeaturesAppointmentsBookingProgressTracker
          :appointment="createdAppointment"
          :show-logic-details="true"
        />
        <div class="flex flex-col sm:flex-row justify-end gap-3">
          <NuxtLink
            :to="`/patient/appointments/${createdAppointment.id}`"
            class="btn btn-primary flex items-center justify-center gap-2"
          >
            <LucideActivity class="h-4 w-4" />
            <span>Open Dedicated Tracking Page &rarr;</span>
          </NuxtLink>
          <NuxtLink
            to="/patient/appointments"
            class="btn btn-secondary flex items-center justify-center gap-2"
          >
            <span>View All My Appointments</span>
          </NuxtLink>
        </div>
      </div>

      <!-- Fallback Success Banner -->
      <div v-else-if="bookingSuccess" class="bg-green-50 border border-green-200 rounded-xl p-6 space-y-3">
        <div class="flex items-center gap-3 text-green-800">
          <LucideCheckCircle2 class="h-6 w-6 text-green-600 shrink-0" />
          <div>
            <h3 class="text-lg font-bold">Appointment Request Submitted!</h3>
            <p class="text-xs text-green-700 mt-0.5">Your reference number is <strong class="font-mono text-sm underline">{{ bookingSuccess.reference }}</strong></p>
          </div>
        </div>
        <div class="text-xs text-green-700 bg-white p-3 rounded-lg border border-green-200 flex items-center justify-between">
          <span>Scheduled for: <strong>{{ bookingSuccess.date }}</strong> at <strong>{{ bookingSuccess.time }}</strong></span>
          <NuxtLink to="/patient/appointments" class="text-primary-600 font-semibold hover:underline">
            View My Appointments &rarr;
          </NuxtLink>
        </div>
      </div>

      <!-- Top Profile Banner -->
      <div class="card !p-0 overflow-hidden">
        <div class="p-8 border-b border-gray-200 flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <div class="h-24 w-24 rounded-full overflow-hidden bg-primary-50 border-2 border-primary-200 flex items-center justify-center shrink-0">
            <BaseAvatar :src="doctorsStore.currentDoctor.profile_image_url" :alt="`Dr. ${doctorsStore.currentDoctor.user.name}`" fallback="/images/public-doctor-fallback.svg" />
          </div>

          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span v-if="doctorsStore.currentDoctor.title" class="px-2.5 py-0.5 rounded text-xs font-semibold bg-primary-100 text-primary-800">
                {{ doctorsStore.currentDoctor.title }}
              </span>
              <span class="px-2.5 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-green-600"></span>
                Active Specialist
              </span>
            </div>

            <h1 class="text-3xl font-bold text-gray-900">
              Dr. {{ doctorsStore.currentDoctor.user.name }}
            </h1>

            <p v-if="doctorsStore.currentDoctor.specialty" class="text-base text-teal-600 font-medium flex items-center gap-1.5">
              <LucideActivity class="h-4 w-4" />
              <span>{{ doctorsStore.currentDoctor.specialty.name }}</span>
            </p>
          </div>
        </div>

        <!-- Detail Info -->
        <div class="p-8 space-y-6">
          <div>
            <h2 class="text-lg font-semibold text-gray-900 mb-2">About Dr. {{ doctorsStore.currentDoctor.user.name }}</h2>
            <p v-if="doctorsStore.currentDoctor.bio" class="text-gray-700 leading-relaxed whitespace-pre-line">
              {{ doctorsStore.currentDoctor.bio }}
            </p>
            <p v-else class="text-gray-400 italic">
              No biography details have been added for this doctor profile.
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-6 border-t border-gray-100">
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-xs text-gray-500 font-medium mb-1">Email Address</div>
              <div class="text-sm font-semibold text-gray-900 flex items-center gap-2">
                <LucideMail class="h-4 w-4 text-gray-400" />
                <span>{{ doctorsStore.currentDoctor.user.email }}</span>
              </div>
            </div>

            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div class="text-xs text-gray-500 font-medium mb-1">Contact Phone</div>
              <div class="text-sm font-semibold text-gray-900 flex items-center gap-2">
                <LucidePhone class="h-4 w-4 text-gray-400" />
                <span>{{ doctorsStore.currentDoctor.phone || 'Not provided' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Real Appointment Booking Widget -->
      <div class="card p-8 space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-200">
          <div>
            <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
              <LucideCalendarCheck class="h-5 w-5 text-primary-600" />
              <span>Book an Appointment</span>
            </h2>
            <p class="text-xs text-gray-500 mt-1">Select date and time slot to schedule your consultation</p>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <!-- Service Selector -->
            <div v-if="compatibleServices.length > 0" class="w-full sm:w-48">
              <label class="form-label mb-1">Clinic Service</label>
              <select v-model="selectedServiceId" class="form-input w-full text-xs">
                <option value="">General Consultation</option>
                <option v-for="srv in compatibleServices" :key="srv.id" :value="srv.id">{{ srv.name }}</option>
              </select>
            </div>

          </div>
        </div>

        <!-- Live Booking Setup Progress Indicator -->
        <div class="rounded-xl border border-primary-200 bg-gradient-to-r from-primary-50 via-white to-teal-50 p-4 shadow-sm space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-primary-100 pb-2.5">
            <div class="flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded-full bg-primary-600 text-white text-xs font-bold">
                <LucideActivity class="h-3.5 w-3.5" />
              </span>
              <h3 class="text-xs font-bold text-gray-900 uppercase tracking-wide">
                Live Booking Setup Progress
              </h3>
            </div>
            <span class="text-xs font-semibold text-primary-800 bg-white px-3 py-1 rounded-full border border-primary-200">
              {{ selectedSlot ? 'Step 3: Slot Selected & Ready' : selectedDate ? 'Step 2: Date Chosen' : 'Step 1: Choose Date' }}
            </span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <!-- 1. Doctor & Service -->
            <div class="rounded-lg bg-white p-2.5 border border-primary-100 shadow-2xs space-y-0.5">
              <div class="flex items-center gap-1.5 font-bold text-teal-700 text-[11px]">
                <LucideCheckCircle2 class="h-3.5 w-3.5 text-teal-600" />
                <span>1. Provider & Service</span>
              </div>
              <p class="text-[11px] text-gray-900 truncate font-semibold">Dr. {{ doctorsStore.currentDoctor.user.name }}</p>
              <p class="text-[10px] text-gray-500 truncate">{{ selectedServiceName }}</p>
            </div>

            <!-- 2. Consultation Date -->
            <div
              class="rounded-lg p-2.5 border shadow-2xs space-y-0.5 transition-all"
              :class="selectedDate ? 'bg-white border-primary-200 ring-2 ring-primary-100' : 'bg-gray-50 border-gray-200 opacity-60'"
            >
              <div class="flex items-center gap-1.5 font-bold text-[11px]" :class="selectedDate ? 'text-teal-700' : 'text-gray-500'">
                <LucideCheckCircle2 v-if="selectedDate" class="h-3.5 w-3.5 text-teal-600" />
                <LucideClock v-else class="h-3.5 w-3.5 text-gray-400" />
                <span>2. Consultation Date</span>
              </div>
              <p class="text-[11px] font-semibold text-gray-900 truncate">{{ formatLongDate(selectedDate) || 'Pick date on calendar' }}</p>
              <p class="text-[10px] text-gray-500 truncate">
                {{ schedulesStore.availability?.slots?.length ? `${schedulesStore.availability.slots.length} slots available` : 'Select date below' }}
              </p>
            </div>

            <!-- 3. Time Slot -->
            <div
              class="rounded-lg p-2.5 border shadow-2xs space-y-0.5 transition-all"
              :class="selectedSlot ? 'bg-white border-teal-300 ring-2 ring-teal-100' : 'bg-amber-50/70 border-amber-200'"
            >
              <div class="flex items-center gap-1.5 font-bold text-[11px]" :class="selectedSlot ? 'text-teal-700' : 'text-amber-700 animate-pulse'">
                <LucideCheckCircle2 v-if="selectedSlot" class="h-3.5 w-3.5 text-teal-600" />
                <LucideClock v-else class="h-3.5 w-3.5 text-amber-500" />
                <span>3. Time Slot</span>
              </div>
              <p class="text-[11px] font-semibold font-mono text-gray-900 truncate">
                {{ selectedSlot || 'Choose slot below' }}
              </p>
              <p class="text-[10px] text-gray-500 truncate">
                {{ selectedSlot ? 'Slot locked' : 'Click time slot' }}
              </p>
            </div>

            <!-- 4. Clinic Approval -->
            <div class="rounded-lg bg-gray-50 p-2.5 border border-gray-200 shadow-2xs space-y-0.5 opacity-80">
              <div class="flex items-center gap-1.5 font-bold text-gray-600 text-[11px]">
                <LucideUserCheck class="h-3.5 w-3.5 text-gray-400" />
                <span>4. Clinic Approval</span>
              </div>
              <p class="text-[11px] font-semibold text-gray-800">Staff / Assistant</p>
              <p class="text-[10px] text-gray-500">Confirms after submit</p>
            </div>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 bg-gray-50 p-4">
          <div class="mb-4 flex items-center justify-between">
            <button type="button" class="btn btn-secondary !px-3" aria-label="Previous month" @click="changeMonth(-1)"><LucideChevronLeft class="h-4 w-4" /></button>
            <h3 class="font-semibold text-gray-900">{{ monthLabel }}</h3>
            <button type="button" class="btn btn-secondary !px-3" aria-label="Next month" @click="changeMonth(1)"><LucideChevronRight class="h-4 w-4" /></button>
          </div>
          <div class="grid grid-cols-7 gap-1 text-center">
            <div v-for="dayName in calendarWeekdays" :key="dayName" class="py-1 text-[10px] font-bold uppercase text-gray-500">{{ dayName }}</div>
            <div v-for="(day, index) in calendarDays" :key="day?.date || `blank-${index}`" class="aspect-square">
              <button
                v-if="day"
                type="button"
                :disabled="day.date < todayStr || day.slots.length === 0"
                class="flex h-full w-full flex-col items-center justify-center rounded-lg border text-xs transition-colors disabled:cursor-not-allowed"
                :class="selectedDate === day.date ? 'border-primary-600 bg-primary-600 text-white font-bold shadow-sm' : day.date < todayStr ? 'border-transparent text-gray-300' : day.slots.length ? 'border-green-300 bg-green-50 font-semibold text-green-800 hover:border-green-500 hover:bg-green-100/60' : day.is_working_day ? 'border-red-200 bg-red-50 font-semibold text-red-600' : 'border-gray-200 bg-white text-gray-400'"
                @click="selectAvailabilityDay(day.date)"
              >
                <span>{{ Number(day.date.slice(-2)) }}</span>
                <span v-if="day.slots.length" class="mt-0.5 text-[9px] font-semibold">{{ day.slots.length }} left</span>
                <span v-else-if="day.is_working_day && day.date >= todayStr" class="mt-0.5 text-[8px] font-bold uppercase tracking-tight text-red-600">Full</span>
              </button>
            </div>
          </div>
          <div class="mt-3 flex flex-wrap gap-4 text-[10px] text-gray-600">
            <span class="flex items-center gap-1.5"><i class="inline-block h-2.5 w-2.5 rounded bg-green-100 ring-1 ring-green-300"></i>Green &ndash; Available (slots left)</span>
            <span class="flex items-center gap-1.5"><i class="inline-block h-2.5 w-2.5 rounded bg-red-100 ring-1 ring-red-300"></i>Red &ndash; Fully booked</span>
            <span class="flex items-center gap-1.5"><i class="inline-block h-2.5 w-2.5 rounded bg-white ring-1 ring-gray-300"></i>Gray &ndash; Unavailable / Day off</span>
          </div>
          <p class="mt-2 text-[11px] text-gray-500 italic">
            Doctor's schedule: Slots are provided according to Dr. {{ doctorsStore.currentDoctor.user.name }}'s working hours. All requested appointments require clinic confirmation.
          </p>
        </div>

        <!-- Availability Loading State -->
        <div v-if="schedulesStore.loading" class="flex justify-center py-12">
          <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
        </div>

        <!-- Availability Slot Selection -->
        <div v-else-if="schedulesStore.availability" class="space-y-6">
          <div v-if="!schedulesStore.availability.is_working_day || schedulesStore.availability.slots.length === 0" class="p-8 text-center bg-gray-50 rounded-xl border border-gray-200">
            <LucideCalendarX class="h-10 w-10 text-gray-400 mx-auto mb-2" />
            <h4 class="text-base font-semibold text-gray-900">No Available Time Slots</h4>
            <p class="text-xs text-gray-500 mt-1">Doctor is unavailable or all slots are booked on {{ selectedDate }}. Please choose another date.</p>
          </div>

          <div v-else class="space-y-4">
            <div class="flex items-center justify-between text-xs text-gray-600 font-medium">
              <span>Select an Available Time Slot</span>
              <span class="text-green-700 bg-green-50 px-2 py-0.5 rounded border border-green-200">
                {{ schedulesStore.availability.slots.length }} Slots Available
              </span>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              <button
                v-for="slot in schedulesStore.availability.slots"
                :key="slot.start_time"
                type="button"
                class="px-3 py-2.5 rounded-lg border text-sm font-mono font-medium transition-all text-center"
                :class="selectedSlot === slot.start_time ? 'bg-primary-600 text-white border-primary-600 shadow-md scale-102' : 'bg-white text-gray-800 border-gray-200 hover:border-primary-300 hover:bg-primary-50/50'"
                @click="selectedSlot = slot.start_time"
              >
                {{ slot.start_time }} &mdash; {{ slot.end_time }}
              </button>
            </div>

            <div v-if="selectedSlot" class="pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-teal-50/60 p-4 rounded-xl border border-teal-200">
              <div class="text-xs text-gray-700 space-y-0.5">
                <span class="font-bold text-gray-900 text-sm block">
                  {{ formatLongDate(selectedDate) }} at {{ selectedSlot }}
                </span>
                <span class="text-gray-600">Service: <strong>{{ selectedServiceName }}</strong></span>
                <span class="text-[11px] text-teal-800 block font-medium">
                  &bull; Once submitted, Clinic Staff / Doctor Assistant will review and confirm this slot.
                </span>
              </div>
              <div class="flex flex-wrap gap-2.5 sm:justify-end">
                <button
                  type="button"
                  class="btn btn-primary flex items-center gap-1.5"
                  @click="handleOpenBookingModal"
                >
                  <LucideCalendarCheck class="h-4 w-4" />
                  <span>Quick Book ({{ selectedSlot }})</span>
                </button>
                <button
                  type="button"
                  class="btn btn-secondary flex items-center gap-1.5"
                  @click="handleInitiateBooking"
                >
                  <span>Review Notes &rarr;</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- BOOKING CONFIRMATION MODAL -->
    <div v-if="showBookingModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Confirm appointment booking" @click.self="showBookingModal = false">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Confirm Appointment Booking</h3>

        <div v-if="bookingError" class="bg-red-50 text-red-700 p-3 rounded-lg text-xs flex items-center gap-2">
          <LucideAlertCircle class="h-4 w-4 text-red-500 shrink-0" />
          <span>{{ bookingError }}</span>
        </div>

        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-2 text-sm">
          <div class="flex flex-col gap-1 sm:flex-row sm:justify-between">
            <span class="text-gray-500">Doctor:</span>
            <span class="font-semibold text-gray-900">Dr. {{ doctorsStore.currentDoctor?.user.name }}</span>
          </div>
          <div class="flex flex-col gap-1 sm:flex-row sm:justify-between">
            <span class="text-gray-500">Date:</span>
            <span class="font-semibold text-gray-900">{{ selectedDate }}</span>
          </div>
          <div class="flex flex-col gap-1 sm:flex-row sm:justify-between">
            <span class="text-gray-500">Time:</span>
            <span class="font-semibold text-gray-900 font-mono">{{ selectedSlot }}</span>
          </div>
        </div>

        <div class="rounded-lg bg-blue-50 border border-blue-200 p-3 text-xs text-blue-900 flex items-start gap-2">
          <LucideInfo class="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
          <p>
            Your booking will be placed in <strong>Pending</strong> status and confirmed by <strong>Clinic Staff / Doctor Assistant</strong>.
          </p>
        </div>

        <div>
          <label class="form-label mb-1">Reason for Visit / Symptoms (Optional)</label>
          <textarea
            v-model="reasonInput"
            rows="3"
            placeholder="Brief description of concern..."
            class="form-input w-full"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showBookingModal = false">Cancel</button>
          <button
            type="button"
            :disabled="isSubmitting"
            class="btn btn-primary flex items-center gap-2"
            @click="handleConfirmBooking"
          >
            <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin" />
            <span>Complete Booking</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
