<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { useAppointmentsStore } from '~/stores/appointments'
import { useDoctorsStore } from '~/stores/doctors'
import { useSpecialtiesStore } from '~/stores/specialties'
import { useClinicServicesStore } from '~/stores/clinicServices'
import { useSchedulesStore } from '~/stores/schedules'
import { useSchedulesService } from '~/services/schedules'
import { usePatientService } from '~/services/patient'
import { normalizePhilippineMobile } from '~/utils/phone'
import type { Doctor } from '~~/shared/types/Doctor'
import type { AppointmentRead } from '~~/shared/types/Appointment'
import { WEEKDAYS } from '~~/shared/types/Schedule'
import type { DoctorSchedule, TimeSlot } from '~~/shared/types/Schedule'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appointmentsStore = useAppointmentsStore()
const doctorsStore = useDoctorsStore()
const specialtiesStore = useSpecialtiesStore()
const servicesStore = useClinicServicesStore()
const schedulesStore = useSchedulesStore()
const schedulesService = useSchedulesService()
const patientService = usePatientService()

const allDoctorSchedulesMap = ref<Record<string, DoctorSchedule[]>>({})

// Stepper state: 1 through 6 (Same structure as poiseathome)
const step = ref<number>(1)
const stepLabels = [
  'Patient Info',
  'Doctor & Schedule',
  'Symptoms & Details',
  'Review',
  'Confirm',
  'Print Slip',
]

// Global loading & messages
const loading = ref(true)
const isSubmitting = ref(false)
const error = ref<string | null>(null)

// STEP 1: Patient Information State
const patientForm = reactive({
  name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: '',
  address: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
})
const patientErrors = reactive<Record<string, string>>({})
const isUpdatingProfile = ref(false)

// STEP 2: Doctor & Schedule Selection State
const selectedSpecialtyId = ref<string>('')
const doctorSearchQuery = ref<string>('')
const selectedDoctor = ref<Doctor | null>(null)
const selectedDate = ref<string>('')
const selectedTime = ref<string>('')
const loadingSlots = ref(false)
const slots = ref<TimeSlot[]>([])
const isWorkingDay = ref(true)

// STEP 3: Booking Details & Symptoms State
const selectedServiceId = ref<string>('')
const symptoms = ref<string>('')
const symptomDuration = ref<string>('1–3 days')
const medicalNotes = ref<string>('')
const symptomError = ref<string | null>(null)

const commonSymptomChips = [
  'Fever & Chills',
  'Persistent Headache',
  'Cough & Cold',
  'Sore Throat',
  'Abdominal Pain',
  'Chest Discomfort',
  'Joint / Muscle Pain',
  'Skin Rash / Allergy',
  'Routine Health Checkup',
  'Prescription Refill',
  'Medical Clearance',
]

// STEP 5: Confirm Agreement
const confirmAgreed = ref(false)

// STEP 6: Created Appointment Result
const createdAppointment = ref<AppointmentRead | null>(null)

// Date Helpers
const getTodayStr = () => {
  const d = new Date()
  const yr = d.getFullYear()
  const mo = String(d.getMonth() + 1).padStart(2, '0')
  const da = String(d.getDate()).padStart(2, '0')
  return `${yr}-${mo}-${da}`
}

const getFutureDateStr = (daysAhead: number) => {
  const d = new Date()
  d.setDate(d.getDate() + daysAhead)
  const yr = d.getFullYear()
  const mo = String(d.getMonth() + 1).padStart(2, '0')
  const da = String(d.getDate()).padStart(2, '0')
  return `${yr}-${mo}-${da}`
}

const formatDateLong = (dateStr: string) => {
  if (!dateStr) return 'Not selected'
  const [year, month, day] = dateStr.split('-').map(Number)
  if (!year || !month || !day) return dateStr
  const d = new Date(year, month - 1, day)
  return d.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

const formatTime12h = (timeStr: string) => {
  if (!timeStr) return ''
  const [h, m] = timeStr.split(':').map(Number)
  if (isNaN(h) || isNaN(m)) return timeStr
  const period = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 || 12
  return `${hour12}:${String(m).padStart(2, '0')} ${period}`
}

const formatQuickDate = (dateStr: string) => {
  if (!dateStr) return ''
  const [year, month, day] = dateStr.split('-').map(Number)
  if (!year || !month || !day) return dateStr
  const d = new Date(year, month - 1, day)
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

const getDoctorWorkingDaysText = (doctorId: string) => {
  const schs = allDoctorSchedulesMap.value[doctorId]?.filter(s => s.is_active) || []
  if (!schs.length) return 'No schedule set'
  const days = schs.map(s => WEEKDAYS[s.day_of_week]).filter(Boolean)
  const uniqueDays = Array.from(new Set(days))
  return uniqueDays.join(', ')
}

const selectedDoctorSchedules = computed(() => {
  if (!selectedDoctor.value) return []
  return allDoctorSchedulesMap.value[selectedDoctor.value.id]?.filter(s => s.is_active) || []
})

const workingDaysSummary = computed(() => {
  if (!selectedDoctorSchedules.value.length) return 'No clinic hours configured'
  return selectedDoctorSchedules.value
    .map(s => `${WEEKDAYS[s.day_of_week]} (${s.start_time}–${s.end_time})`)
    .join(', ')
})

const isDoctorWorkingOnDate = (dateStr: string) => {
  if (!dateStr || !selectedDoctor.value) return false
  const schs = selectedDoctorSchedules.value
  if (!schs.length) return false
  const [year, month, day] = dateStr.split('-').map(Number)
  if (!year || !month || !day) return false
  const d = new Date(year, month - 1, day)
  const scheduleDay = (d.getDay() + 6) % 7
  return schs.some(s => s.day_of_week === scheduleDay)
}

const getUpcomingWorkingDates = (doctorId: string, maxCount = 4): string[] => {
  const schs = allDoctorSchedulesMap.value[doctorId]?.filter(s => s.is_active) || []
  if (!schs.length) return []
  const workingDaySet = new Set(schs.map(s => s.day_of_week))

  const dates: string[] = []
  const today = new Date()
  const nowH = String(today.getHours()).padStart(2, '0')
  const nowM = String(today.getMinutes()).padStart(2, '0')
  const nowTime = `${nowH}:${nowM}`

  for (let offset = 0; offset < 60 && dates.length < maxCount; offset++) {
    const d = new Date()
    d.setDate(d.getDate() + offset)
    const yr = d.getFullYear()
    const mo = String(d.getMonth() + 1).padStart(2, '0')
    const da = String(d.getDate()).padStart(2, '0')
    const dateStr = `${yr}-${mo}-${da}`

    const scheduleDay = (d.getDay() + 6) % 7
    if (workingDaySet.has(scheduleDay)) {
      if (offset === 0) {
        const todaySchs = schs.filter(s => s.day_of_week === scheduleDay)
        if (todaySchs.some(s => s.end_time > nowTime)) {
          dates.push(dateStr)
        }
      } else {
        dates.push(dateStr)
      }
    }
  }
  return dates
}

const upcomingWorkingDates = computed(() => {
  if (!selectedDoctor.value) return []
  return getUpcomingWorkingDates(selectedDoctor.value.id, 4)
})

const nextAvailableWorkingDate = computed(() => {
  if (!selectedDoctor.value) return null
  const dates = getUpcomingWorkingDates(selectedDoctor.value.id, 1)
  return dates[0] || null
})

// Computed: Filtered Doctors
const filteredDoctors = computed(() => {
  return doctorsStore.doctors.filter(doc => {
    if (!doc.is_active) return false
    if (selectedSpecialtyId.value && doc.specialty_id !== selectedSpecialtyId.value) {
      return false
    }
    if (doctorSearchQuery.value.trim()) {
      const q = doctorSearchQuery.value.toLowerCase()
      const nameMatch = doc.user.name.toLowerCase().includes(q)
      const specMatch = doc.specialty?.name.toLowerCase().includes(q) || false
      const titleMatch = doc.title?.toLowerCase().includes(q) || false
      if (!nameMatch && !specMatch && !titleMatch) return false
    }
    return true
  })
})

// Morning & Afternoon slots grouping
const morningSlots = computed(() => {
  return slots.value.filter(slot => {
    const hour = parseInt(slot.start_time.split(':')[0], 10)
    return hour < 12
  })
})

const afternoonSlots = computed(() => {
  return slots.value.filter(slot => {
    const hour = parseInt(slot.start_time.split(':')[0], 10)
    return hour >= 12
  })
})

const selectedServiceName = computed(() => {
  if (!selectedServiceId.value) return 'General Consultation'
  const s = servicesStore.services.find(item => item.id === selectedServiceId.value)
  return s ? s.name : 'General Consultation'
})

// Initialize Data
onMounted(async () => {
  try {
    loading.value = true
    await Promise.all([
      doctorsStore.fetchDoctors(true),
      specialtiesStore.fetchSpecialties(true),
      servicesStore.fetchServices(true),
    ])

    // Pre-load schedules for doctors to show working day badges
    try {
      const schResults = await Promise.all(
        doctorsStore.doctors.map(async (doc) => {
          const schs = await schedulesService.getDoctorSchedules(doc.id)
          return [doc.id, schs] as const
        }),
      )
      allDoctorSchedulesMap.value = Object.fromEntries(schResults)
    } catch {
      // non-blocking
    }

    // Load Patient Profile
    try {
      const profile = await patientService.getMyProfile()
      patientForm.name = profile.user.name || authStore.user?.name || ''
      patientForm.email = profile.user.email || authStore.user?.email || ''
      patientForm.phone = profile.phone || ''
      patientForm.date_of_birth = profile.date_of_birth || ''
      patientForm.gender = profile.gender || ''
      patientForm.address = profile.address || ''
    } catch {
      if (authStore.user) {
        patientForm.name = authStore.user.name || ''
        patientForm.email = authStore.user.email || ''
      }
    }

    // Check query params
    const qDoctorId = String(route.query.doctor || '')
    const qDate = String(route.query.date || '')
    const qTime = String(route.query.time || '')
    const qService = String(route.query.service || '')

    if (qDoctorId) {
      const foundDoc = doctorsStore.doctors.find(d => d.id === qDoctorId)
      if (foundDoc) {
        selectedDoctor.value = foundDoc
        if (foundDoc.specialty_id) {
          selectedSpecialtyId.value = foundDoc.specialty_id
        }
      }
    }

    if (qDate && qDate >= getTodayStr()) {
      selectedDate.value = qDate
    } else if (selectedDoctor.value && nextAvailableWorkingDate.value) {
      selectedDate.value = nextAvailableWorkingDate.value
    } else {
      selectedDate.value = getTodayStr()
    }

    if (qTime) selectedTime.value = qTime
    if (qService) selectedServiceId.value = qService

    if (selectedDoctor.value && selectedDate.value) {
      await loadSlots(selectedDoctor.value.id, selectedDate.value)
    }
  } catch (err: any) {
    error.value = err?.data?.detail || 'Failed to initialize booking.'
  } finally {
    loading.value = false
  }
})

// Load Doctor Availability
const loadSlots = async (doctorId: string, dateStr: string) => {
  if (!doctorId || !dateStr) {
    slots.value = []
    return
  }
  loadingSlots.value = true
  try {
    const res = await schedulesStore.fetchAvailability(doctorId, dateStr)
    if (res) {
      slots.value = res.slots || []
      isWorkingDay.value = res.is_working_day
    } else {
      slots.value = []
      isWorkingDay.value = false
    }
  } catch {
    slots.value = []
    isWorkingDay.value = false
  } finally {
    loadingSlots.value = false
  }
}

watch([selectedDoctor, selectedDate], async ([newDoc, newDate]) => {
  if (newDoc && newDate) {
    selectedTime.value = ''
    await loadSlots(newDoc.id, newDate)
  } else {
    slots.value = []
  }
})

const handleSelectDoctor = async (doc: Doctor) => {
  selectedDoctor.value = doc
  selectedTime.value = ''

  if (!allDoctorSchedulesMap.value[doc.id]) {
    try {
      const schs = await schedulesService.getDoctorSchedules(doc.id)
      allDoctorSchedulesMap.value[doc.id] = schs
    } catch {
      allDoctorSchedulesMap.value[doc.id] = []
    }
  }

  const nextDate = nextAvailableWorkingDate.value
  if (nextDate && (!selectedDate.value || !isDoctorWorkingOnDate(selectedDate.value) || (selectedDate.value === getTodayStr() && !upcomingWorkingDates.value.includes(getTodayStr())))) {
    selectedDate.value = nextDate
  } else if (!selectedDate.value) {
    selectedDate.value = nextDate || getTodayStr()
  }

  await loadSlots(doc.id, selectedDate.value)
}

const addSymptomChip = (chip: string) => {
  if (!symptoms.value.trim()) {
    symptoms.value = chip
  } else if (!symptoms.value.includes(chip)) {
    symptoms.value = `${symptoms.value.trim()}, ${chip}`
  }
}

// STEP 1 VALIDATE & CONTINUE
const handleStep1Continue = async () => {
  Object.keys(patientErrors).forEach(key => delete patientErrors[key])
  let isValid = true

  if (!patientForm.name.trim()) {
    patientErrors.name = 'Full name is required'
    isValid = false
  }
  if (!patientForm.phone.trim()) {
    patientErrors.phone = 'Phone number is required'
    isValid = false
  }
  if (!patientForm.date_of_birth) {
    patientErrors.date_of_birth = 'Date of birth is required'
    isValid = false
  }
  if (!patientForm.gender) {
    patientErrors.gender = 'Gender is required'
    isValid = false
  }
  if (!patientForm.address.trim()) {
    patientErrors.address = 'Address is required'
    isValid = false
  }

  if (!isValid) return

  try {
    isUpdatingProfile.value = true
    await patientService.updateMyProfile({
      name: patientForm.name.trim(),
      phone: normalizePhilippineMobile(patientForm.phone) || patientForm.phone.trim(),
      date_of_birth: patientForm.date_of_birth,
      gender: patientForm.gender,
      address: patientForm.address.trim(),
    })
    if (authStore.user) {
      authStore.user.name = patientForm.name.trim()
    }
  } catch (err) {
    console.warn('Profile sync:', err)
  } finally {
    isUpdatingProfile.value = false
  }

  step.value = 2
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// STEP 2 VALIDATE & CONTINUE
const handleStep2Continue = () => {
  if (!selectedDoctor.value || !selectedDate.value || !selectedTime.value) {
    error.value = 'Please select a doctor, consultation date, and available time slot.'
    return
  }
  error.value = null
  step.value = 3
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// STEP 3 VALIDATE & CONTINUE
const handleStep3Continue = () => {
  symptomError.value = null
  if (!symptoms.value.trim() || symptoms.value.trim().length < 5) {
    symptomError.value = 'Please describe your symptoms or reason for visit (minimum 5 characters).'
    return
  }
  step.value = 4
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// STEP 4 CONTINUE TO 5
const handleStep4Continue = () => {
  confirmAgreed.value = false
  step.value = 5
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// STEP 5: FINAL SUBMIT BOOKING
const handleFinalBookingSubmit = async () => {
  if (!selectedDoctor.value || !selectedDate.value || !selectedTime.value) {
    error.value = 'Doctor or schedule details missing.'
    return
  }
  if (!confirmAgreed.value) {
    error.value = 'Please check the agreement box before completing the booking.'
    return
  }

  isSubmitting.value = true
  error.value = null

  const fullReason = [
    `Symptoms: ${symptoms.value.trim()}`,
    `Duration: ${symptomDuration.value}`,
    medicalNotes.value.trim() ? `Notes: ${medicalNotes.value.trim()}` : null,
  ]
    .filter(Boolean)
    .join(' | ')
    .slice(0, 500)

  try {
    const res = await appointmentsStore.createAppointment({
      doctor_profile_id: selectedDoctor.value.id,
      service_id: selectedServiceId.value || null,
      date: selectedDate.value,
      time: selectedTime.value,
      reason: fullReason,
    })

    createdAppointment.value = res
    step.value = 6
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err: any) {
    error.value =
      err?.data?.detail ||
      'Failed to complete booking. That slot may have just been taken. Please choose another slot.'
  } finally {
    isSubmitting.value = false
  }
}

const handlePrintSlip = () => {
  window.print()
}
</script>

<template>
  <div class="min-h-screen bg-[#f4f8fb] font-sans text-gray-900">
    <!-- Top Bar Navigation (like poiseathome) -->
    <header class="border-b border-teal-100 bg-white no-print">
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <NuxtLink to="/patient/dashboard" class="flex items-center gap-2.5">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-700 text-white font-bold text-base shadow-sm">
            +
          </div>
          <span class="text-lg font-bold tracking-tight text-gray-900">SMMG Healthcare</span>
        </NuxtLink>

        <NuxtLink to="/patient/appointments" class="text-sm font-semibold text-primary-700 hover:text-primary-800 hover:underline flex items-center gap-1.5">
          <LucideCalendar class="h-4 w-4" />
          <span>My Appointments</span>
        </NuxtLink>
      </div>
    </header>

    <div class="mx-auto max-w-5xl px-4 py-7 sm:px-6 sm:py-10">
      <!-- Back Link -->
      <NuxtLink
        to="/patient/dashboard"
        class="mb-7 inline-flex items-center text-sm font-medium text-gray-500 transition-colors hover:text-primary-700 no-print"
      >
        <LucideArrowLeft class="mr-1.5 h-4 w-4" /> Back to Dashboard
      </NuxtLink>

      <!-- STEPPER HEADER HERO BANNER (Direct poiseathome aesthetic) -->
      <div v-if="step < 6" class="mb-7 overflow-hidden rounded-3xl border border-teal-100 bg-white shadow-sm no-print">
        <div class="relative overflow-hidden bg-[#0a2540] px-6 py-7 text-white sm:px-8">
          <div class="absolute -right-12 -top-16 h-48 w-48 rounded-full bg-teal-500/25 blur-3xl" />
          <div class="relative">
            <p class="flex items-center gap-2 text-xs font-bold uppercase tracking-[.16em] text-teal-300">
              <LucideStethoscope class="h-4 w-4" /> Healthcare Consultation Booking
            </p>
            <h1 class="mt-2 text-3xl font-bold tracking-tight">Build your appointment</h1>
            <p class="mt-2 max-w-xl text-sm leading-6 text-white/80">
              Follow our guided stepper to confirm your information, select your doctor, schedule consultation, and print your appointment slip.
            </p>
          </div>
        </div>

        <!-- Stepper Numbers Bar (Exact poiseathome style) -->
        <ol class="grid grid-cols-3 sm:grid-cols-6 gap-1 px-3 py-5 sm:px-8" aria-label="Booking progress">
          <li
            v-for="(label, idx) in stepLabels"
            :key="idx"
            class="min-w-0 text-center"
            :aria-current="step === idx + 1 ? 'step' : undefined"
          >
            <button
              type="button"
              :disabled="idx + 1 > step"
              class="w-full focus:outline-none"
              @click="idx + 1 < step && (step = idx + 1)"
            >
              <div
                class="mx-auto flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold transition"
                :class="[
                  step === idx + 1
                    ? 'bg-primary-600 text-white shadow-md shadow-primary-200 ring-2 ring-primary-300'
                    : step > idx + 1
                    ? 'bg-teal-100 text-teal-700'
                    : 'bg-gray-100 text-gray-400',
                ]"
              >
                <LucideCheckCircle2 v-if="step > idx + 1" class="w-4 h-4" />
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <span
                class="mt-2 block truncate text-xs"
                :class="[
                  step === idx + 1
                    ? 'font-semibold text-primary-900'
                    : step > idx + 1
                    ? 'font-medium text-gray-800'
                    : 'text-gray-400',
                ]"
              >
                {{ label }}
              </span>
            </button>
          </li>
        </ol>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="mb-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 no-print flex items-center justify-between">
        <span>{{ error }}</span>
        <button type="button" class="text-xs font-bold underline" @click="error = null">Dismiss</button>
      </div>

      <!-- MAIN STEP CONTAINER CARD -->
      <div class="min-h-[420px] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <!-- ========================================================================= -->
        <!-- STEP 1: FILLUP FORM THERE FULL INFO -->
        <!-- ========================================================================= -->
        <div v-if="step === 1" class="p-6 md:p-8">
          <div class="mb-6">
            <p class="text-xs font-bold uppercase tracking-[.15em] text-primary-600">Step 1 of 6</p>
            <h2 class="mt-2 text-2xl font-bold">Patient Information</h2>
            <p class="mt-1 text-sm text-gray-500">Fill up or verify your complete patient details for your clinical record.</p>
          </div>

          <form class="space-y-5" @submit.prevent="handleStep1Continue">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <!-- Full Name -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Full Name <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="patientForm.name"
                  type="text"
                  required
                  placeholder="Juan Dela Cruz"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                  :class="{ 'border-red-400': patientErrors.name }"
                />
                <p v-if="patientErrors.name" class="mt-1 text-xs text-red-600">{{ patientErrors.name }}</p>
              </div>

              <!-- Email -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Email Address <span class="text-xs text-gray-400 font-normal">(Account Login)</span>
                </label>
                <input
                  v-model="patientForm.email"
                  type="email"
                  disabled
                  class="w-full px-4 py-3 border border-gray-200 bg-gray-100/80 rounded-xl text-gray-500 cursor-not-allowed text-sm"
                />
              </div>

              <!-- Phone -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Contact Phone Number <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="patientForm.phone"
                  type="tel"
                  required
                  placeholder="09123456789 or +639123456789"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                  :class="{ 'border-red-400': patientErrors.phone }"
                />
                <p v-if="patientErrors.phone" class="mt-1 text-xs text-red-600">{{ patientErrors.phone }}</p>
              </div>

              <!-- Date of Birth -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Date of Birth <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="patientForm.date_of_birth"
                  type="date"
                  required
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                  :class="{ 'border-red-400': patientErrors.date_of_birth }"
                />
                <p v-if="patientErrors.date_of_birth" class="mt-1 text-xs text-red-600">{{ patientErrors.date_of_birth }}</p>
              </div>

              <!-- Gender -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Gender <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="patientForm.gender"
                  required
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                  :class="{ 'border-red-400': patientErrors.gender }"
                >
                  <option value="" disabled>Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
                <p v-if="patientErrors.gender" class="mt-1 text-xs text-red-600">{{ patientErrors.gender }}</p>
              </div>

              <!-- Address -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Residential Address <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="patientForm.address"
                  type="text"
                  required
                  placeholder="Street, Barangay, City, Province"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                  :class="{ 'border-red-400': patientErrors.address }"
                />
                <p v-if="patientErrors.address" class="mt-1 text-xs text-red-600">{{ patientErrors.address }}</p>
              </div>

              <!-- Emergency Contact Name -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Emergency Contact Name <span class="text-xs text-gray-400 font-normal">(Optional)</span>
                </label>
                <input
                  v-model="patientForm.emergency_contact_name"
                  type="text"
                  placeholder="Maria Dela Cruz (Spouse / Parent)"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>

              <!-- Emergency Contact Phone -->
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-800">
                  Emergency Contact Phone <span class="text-xs text-gray-400 font-normal">(Optional)</span>
                </label>
                <input
                  v-model="patientForm.emergency_contact_phone"
                  type="tel"
                  placeholder="09198765432"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>
            </div>

            <!-- Bottom Navigation Bar -->
            <div class="mt-8 flex items-center justify-between border-t border-gray-100 pt-5">
              <p class="text-xs text-gray-500">
                Patient records are confidential and stored securely.
              </p>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isUpdatingProfile"
              >
                <LucideLoader2 v-if="isUpdatingProfile" class="h-4 w-4 animate-spin" />
                <span>Continue to Doctor & Schedule</span>
                <LucideArrowRight class="h-4 w-4 ml-1.5" />
              </button>
            </div>
          </form>
        </div>

        <!-- ========================================================================= -->
        <!-- STEP 2: DOCTOR FILTER SPECIALIZATION & SCHEDULE -->
        <!-- ========================================================================= -->
        <div v-if="step === 2" class="p-6 md:p-8 space-y-7">
          <div class="mb-2">
            <p class="text-xs font-bold uppercase tracking-[.15em] text-primary-600">Step 2 of 6</p>
            <h2 class="mt-2 text-2xl font-bold">Choose Doctor & Schedule</h2>
            <p class="mt-1 text-sm text-gray-500">Filter by medical specialization and select an available consultation date and time.</p>
          </div>

          <!-- Specialization Filter & Search -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50/80 p-4 rounded-2xl border border-gray-200">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1">
                Filter by Specialization
              </label>
              <select
                v-model="selectedSpecialtyId"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-primary-500 focus:border-primary-500 bg-white"
              >
                <option value="">All Specialties ({{ specialtiesStore.specialties.length }})</option>
                <option v-for="spec in specialtiesStore.specialties" :key="spec.id" :value="spec.id">
                  {{ spec.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1">
                Search Doctor
              </label>
              <div class="relative">
                <input
                  v-model="doctorSearchQuery"
                  type="text"
                  placeholder="Doctor name or keyword..."
                  class="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-primary-500 focus:border-primary-500 bg-white"
                />
                <LucideSearch class="h-4 w-4 text-gray-400 absolute left-3 top-3" />
              </div>
            </div>
          </div>

          <!-- Doctors Selection Cards (Direct poiseathome stylist card layout) -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-bold text-gray-900 text-sm">Qualified Doctors ({{ filteredDoctors.length }})</h3>
              <span v-if="selectedDoctor" class="text-xs text-primary-700 font-semibold">
                Selected: <strong>Dr. {{ selectedDoctor.user.name }}</strong>
              </span>
            </div>

            <div v-if="filteredDoctors.length === 0" class="p-8 text-center bg-gray-50 rounded-xl border border-gray-200">
              <p class="font-semibold text-gray-800">No doctors match your filter</p>
              <p class="text-xs text-gray-500 mt-1">Try selecting "All Specialties" or clearing the search query.</p>
            </div>

            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[340px] overflow-y-auto pr-1">
              <button
                v-for="doc in filteredDoctors"
                :key="doc.id"
                type="button"
                class="flex w-full items-center rounded-2xl border p-4 text-left transition"
                :class="[
                  selectedDoctor?.id === doc.id
                    ? 'border-primary-600 bg-teal-50/60 ring-2 ring-primary-600/30 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-primary-600/50 hover:shadow-sm',
                ]"
                @click="handleSelectDoctor(doc)"
              >
                <div class="w-13 h-13 rounded-full bg-primary-50 border border-primary-200 overflow-hidden flex items-center justify-center mr-4 shrink-0 font-bold text-primary-800">
                  <img v-if="doc.profile_image_url" :src="doc.profile_image_url" class="w-full h-full object-cover" :alt="doc.user.name" />
                  <span v-else>{{ doc.user.name.charAt(0).toUpperCase() }}</span>
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between gap-1">
                    <h4 class="font-bold text-gray-900 text-sm truncate">Dr. {{ doc.user.name }}</h4>
                    <span
                      v-if="selectedDoctor?.id === doc.id"
                      class="text-[10px] font-bold text-white bg-primary-600 px-2 py-0.5 rounded-full shrink-0"
                    >
                      Selected
                    </span>
                  </div>
                  <p class="text-xs font-semibold text-teal-700">{{ doc.specialty?.name || 'Specialist' }}</p>
                  <p v-if="doc.title" class="text-[11px] text-gray-500">{{ doc.title }}</p>
                  <p v-if="doc.bio" class="text-xs text-gray-600 line-clamp-2 mt-1">{{ doc.bio }}</p>
                  <div class="mt-2 flex items-center gap-1.5 text-[11px]">
                    <span
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md font-medium"
                      :class="allDoctorSchedulesMap[doc.id]?.length ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60' : 'bg-gray-100 text-gray-600 border border-gray-200'"
                    >
                      <LucideCalendar class="w-3 h-3 text-emerald-600" />
                      {{ getDoctorWorkingDaysText(doc.id) }}
                    </span>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Schedule & Slots Section (appears when doctor selected) -->
          <div v-if="selectedDoctor" class="rounded-2xl border border-teal-100 bg-teal-50/20 p-5 space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-teal-100/80 pb-3">
              <div>
                <h4 class="font-bold text-gray-900 text-base flex items-center gap-2">
                  <LucideCalendar class="h-4 w-4 text-primary-600" />
                  <span>Choose Date & Time for Dr. {{ selectedDoctor.user.name }}</span>
                </h4>
                <p class="text-xs text-gray-500">Select a date to check real-time consultation slot availability.</p>
              </div>

              <!-- Quick Date presets (Doctor's upcoming working days) -->
              <div v-if="upcomingWorkingDates.length > 0" class="flex flex-wrap items-center gap-1.5">
                <button
                  v-for="wDate in upcomingWorkingDates"
                  :key="wDate"
                  type="button"
                  class="px-2.5 py-1 text-xs font-semibold rounded-lg border transition-colors"
                  :class="selectedDate === wDate ? 'bg-primary-600 text-white border-primary-600 shadow-sm' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-100'"
                  @click="selectedDate = wDate"
                >
                  {{ formatQuickDate(wDate) }}
                  <span v-if="wDate === getTodayStr()" class="ml-1 text-[10px] opacity-80">(Today)</span>
                  <span v-else-if="wDate === getFutureDateStr(1)" class="ml-1 text-[10px] opacity-80">(Tomorrow)</span>
                </button>
              </div>
              <div v-else class="flex items-center gap-1.5">
                <button
                  type="button"
                  class="px-2.5 py-1 text-xs font-semibold rounded-lg border transition-colors"
                  :class="selectedDate === getTodayStr() ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-100'"
                  @click="selectedDate = getTodayStr()"
                >
                  Today
                </button>
                <button
                  type="button"
                  class="px-2.5 py-1 text-xs font-semibold rounded-lg border transition-colors"
                  :class="selectedDate === getFutureDateStr(1) ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-100'"
                  @click="selectedDate = getFutureDateStr(1)"
                >
                  Tomorrow
                </button>
                <button
                  type="button"
                  class="px-2.5 py-1 text-xs font-semibold rounded-lg border transition-colors"
                  :class="selectedDate === getFutureDateStr(2) ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-100'"
                  @click="selectedDate = getFutureDateStr(2)"
                >
                  +2 Days
                </button>
              </div>
            </div>

            <!-- Doctor Clinic Schedule Info Banner -->
            <div class="bg-white rounded-xl p-3 border border-teal-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <div class="flex items-center gap-2 text-gray-700">
                <LucideClock class="w-4 h-4 text-primary-600 shrink-0" />
                <span class="font-medium text-gray-500">Clinic Schedule:</span>
                <span class="font-semibold text-gray-900">{{ workingDaysSummary }}</span>
              </div>
              <div v-if="nextAvailableWorkingDate && selectedDate !== nextAvailableWorkingDate" class="shrink-0">
                <button
                  type="button"
                  class="text-xs text-primary-700 font-bold hover:underline inline-flex items-center gap-1"
                  @click="selectedDate = nextAvailableWorkingDate"
                >
                  Jump to next working day ({{ formatQuickDate(nextAvailableWorkingDate) }}) →
                </button>
              </div>
            </div>

            <!-- Date Picker -->
            <div class="max-w-xs">
              <label class="block text-xs font-semibold text-gray-700 mb-1">Select Consultation Date</label>
              <input
                v-model="selectedDate"
                type="date"
                :min="getTodayStr()"
                class="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm font-medium bg-white focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <!-- Slots Grid (poiseathome style) -->
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-2">
                Available Times for {{ formatDateLong(selectedDate) }}
              </label>

              <div v-if="loadingSlots" class="py-8 text-center text-sm text-gray-500 flex items-center justify-center gap-2">
                <LucideLoader2 class="h-4 w-4 animate-spin text-primary-600" />
                <span>Loading availability slots...</span>
              </div>

              <div v-else-if="!isWorkingDay || slots.length === 0" class="p-6 text-center bg-amber-50/80 rounded-2xl border border-amber-200 text-amber-900 space-y-3">
                <div class="w-10 h-10 mx-auto rounded-full bg-amber-100 text-amber-700 flex items-center justify-center">
                  <LucideCalendarOff class="w-5 h-5" />
                </div>
                <div>
                  <h5 class="font-bold text-sm">No Available Slots on {{ formatDateLong(selectedDate) }}</h5>
                  <p v-if="!selectedDoctorSchedules.length" class="text-xs text-amber-800 mt-1">
                    Dr. {{ selectedDoctor.user.name }} does not currently have clinic hours configured.
                  </p>
                  <p v-else-if="!isDoctorWorkingOnDate(selectedDate)" class="text-xs text-amber-800 mt-1">
                    Dr. {{ selectedDoctor.user.name }} does not hold clinic on this day of the week.
                    <span class="block mt-0.5 font-medium">Regular clinic days: {{ workingDaysSummary }}</span>
                  </p>
                  <p v-else class="text-xs text-amber-800 mt-1">
                    All consultation hours for this date have either passed or have been fully booked.
                  </p>
                </div>
                <div v-if="nextAvailableWorkingDate && nextAvailableWorkingDate !== selectedDate" class="pt-1">
                  <button
                    type="button"
                    class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-xs font-bold rounded-xl transition shadow-sm inline-flex items-center gap-1.5"
                    @click="selectedDate = nextAvailableWorkingDate"
                  >
                    <LucideCalendarCheck class="w-3.5 h-3.5" />
                    <span>Jump to Next Available Date ({{ formatQuickDate(nextAvailableWorkingDate) }})</span>
                  </button>
                </div>
              </div>

              <div v-else class="space-y-4">
                <!-- Morning -->
                <div v-if="morningSlots.length > 0">
                  <p class="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-1.5">Morning (Before 12:00 PM)</p>
                  <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                    <button
                      v-for="slot in morningSlots"
                      :key="slot.start_time"
                      type="button"
                      :disabled="!slot.is_available"
                      class="min-h-10 rounded-xl border px-3 py-2 text-xs font-semibold transition text-center"
                      :class="[
                        selectedTime === slot.start_time
                          ? 'border-primary-600 bg-primary-600 text-white shadow-sm'
                          : slot.is_available
                          ? 'border-gray-200 bg-white text-gray-800 hover:border-primary-600 hover:bg-teal-50/40'
                          : 'border-gray-200 bg-gray-100 text-gray-400 line-through cursor-not-allowed opacity-60',
                      ]"
                      @click="selectedTime = slot.start_time"
                    >
                      <span>{{ formatTime12h(slot.start_time) }}</span>
                    </button>
                  </div>
                </div>

                <!-- Afternoon -->
                <div v-if="afternoonSlots.length > 0">
                  <p class="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-1.5">Afternoon (12:00 PM onwards)</p>
                  <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2">
                    <button
                      v-for="slot in afternoonSlots"
                      :key="slot.start_time"
                      type="button"
                      :disabled="!slot.is_available"
                      class="min-h-10 rounded-xl border px-3 py-2 text-xs font-semibold transition text-center"
                      :class="[
                        selectedTime === slot.start_time
                          ? 'border-primary-600 bg-primary-600 text-white shadow-sm'
                          : slot.is_available
                          ? 'border-gray-200 bg-white text-gray-800 hover:border-primary-600 hover:bg-teal-50/40'
                          : 'border-gray-200 bg-gray-100 text-gray-400 line-through cursor-not-allowed opacity-60',
                      ]"
                      @click="selectedTime = slot.start_time"
                    >
                      <span>{{ formatTime12h(slot.start_time) }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Navigation -->
          <div class="mt-8 flex justify-between border-t border-gray-100 pt-5">
            <button type="button" class="btn btn-ghost" @click="step = 1">
              <LucideArrowLeft class="h-4 w-4 mr-1.5" /> Back
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!selectedDoctor || !selectedDate || !selectedTime"
              @click="handleStep2Continue"
            >
              <span>Continue</span>
              <LucideArrowRight class="h-4 w-4 ml-1.5" />
            </button>
          </div>
        </div>

        <!-- ========================================================================= -->
        <!-- STEP 3: BOOK DETAIL AND PUT SYMPTOMS -->
        <!-- ========================================================================= -->
        <div v-if="step === 3" class="p-6 md:p-8 space-y-6">
          <div class="mb-6">
            <p class="text-xs font-bold uppercase tracking-[.15em] text-primary-600">Step 3 of 6</p>
            <h2 class="mt-2 text-2xl font-bold">Booking Details & Symptoms</h2>
            <p class="mt-1 text-sm text-text-muted text-gray-500">Specify the medical service you require and describe your symptoms for the doctor.</p>
          </div>

          <form class="space-y-6" @submit.prevent="handleStep3Continue">
            <!-- Service Selection -->
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-800">
                Clinic Service / Consultation Type
              </label>
              <select
                v-model="selectedServiceId"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm bg-white"
              >
                <option value="">General Medical Consultation</option>
                <option v-for="srv in servicesStore.services" :key="srv.id" :value="srv.id">
                  {{ srv.name }} {{ srv.description ? `– ${srv.description}` : '' }}
                </option>
              </select>
            </div>

            <!-- Symptoms Input -->
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="block text-sm font-medium text-gray-800">
                  Chief Complaint / Describe Symptoms <span class="text-red-500">*</span>
                </label>
                <span class="text-xs text-gray-400 font-mono">{{ symptoms.length }} / 500</span>
              </div>
              <textarea
                v-model="symptoms"
                rows="4"
                maxlength="500"
                required
                placeholder="Describe your current symptoms, how long you have felt ill, or what you wish to discuss..."
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
                :class="{ 'border-red-400': symptomError }"
              />
              <p v-if="symptomError" class="mt-1 text-xs text-red-600">{{ symptomError }}</p>

              <!-- Symptom Chips (PoiseAtHome quick chips pattern) -->
              <div class="mt-3">
                <p class="text-xs font-semibold text-gray-500 mb-1.5">Quick add common symptoms:</p>
                <div class="flex flex-wrap gap-1.5">
                  <button
                    v-for="chip in commonSymptomChips"
                    :key="chip"
                    type="button"
                    class="px-2.5 py-1 text-xs rounded-lg border border-gray-200 bg-gray-50 text-gray-700 hover:bg-teal-50 hover:border-teal-300 hover:text-teal-800 transition-colors"
                    @click="addSymptomChip(chip)"
                  >
                    + {{ chip }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Duration Options -->
            <div>
              <label class="block text-sm font-medium mb-1.5 text-gray-800">
                Symptom Duration
              </label>
              <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
                <button
                  v-for="d in ['Less than 24h', '1–3 days', '4–7 days', '1–2 weeks', 'Chronic / Ongoing']"
                  :key="d"
                  type="button"
                  class="py-2.5 px-3 text-xs font-semibold rounded-xl border text-center transition-all"
                  :class="[
                    symptomDuration === d
                      ? 'bg-primary-600 text-white border-primary-600 shadow-sm'
                      : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50',
                  ]"
                  @click="symptomDuration = d"
                >
                  {{ d }}
                </button>
              </div>
            </div>

            <!-- Medical Notes / Allergies -->
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-800">
                Allergies or Medical History Notes <span class="text-xs text-gray-400 font-normal">(Optional)</span>
              </label>
              <input
                v-model="medicalNotes"
                type="text"
                maxlength="200"
                placeholder="e.g. Allergy to Penicillin, Diabetic, Hypertension..."
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-primary-500 focus:border-primary-500 text-sm"
              />
            </div>

            <!-- Bottom Navigation -->
            <div class="mt-8 flex justify-between border-t border-gray-100 pt-5">
              <button type="button" class="btn btn-ghost" @click="step = 2">
                <LucideArrowLeft class="h-4 w-4 mr-1.5" /> Back
              </button>
              <button type="submit" class="btn btn-primary">
                <span>Continue to Review</span>
                <LucideArrowRight class="h-4 w-4 ml-1.5" />
              </button>
            </div>
          </form>
        </div>

        <!-- ========================================================================= -->
        <!-- STEP 4: REVIEW BOOKING INFO (Exact poiseathome review card layout) -->
        <!-- ========================================================================= -->
        <div v-if="step === 4" class="p-6 md:p-8">
          <div class="mb-6">
            <p class="text-xs font-bold uppercase tracking-[.15em] text-primary-600">Step 4 of 6</p>
            <h2 class="mt-2 text-2xl font-bold">Review your appointment</h2>
            <p class="mt-1 text-sm text-gray-500">Make sure every detail is correct before proceeding to confirmation.</p>
          </div>

          <!-- poiseathome review container -->
          <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 space-y-5 mb-7">
            <!-- Service & Symptoms block -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <p class="text-sm font-semibold text-gray-500">Consultation Service & Symptoms</p>
                <button type="button" class="text-xs font-semibold text-primary-600 hover:underline" @click="step = 3">
                  Edit
                </button>
              </div>

              <div class="divide-y divide-gray-200 border-y border-gray-200 bg-white rounded-xl p-3">
                <div class="flex justify-between py-2 text-sm">
                  <div>
                    <p class="font-semibold text-gray-900">{{ selectedServiceName }}</p>
                    <p class="text-xs text-gray-500">Duration: {{ symptomDuration }}</p>
                  </div>
                  <span class="font-semibold text-teal-700">30-min session</span>
                </div>
                <div class="py-2.5 text-xs text-gray-700">
                  <span class="font-semibold text-gray-900 block mb-0.5">Symptoms:</span>
                  <p class="leading-relaxed">{{ symptoms }}</p>
                  <p v-if="medicalNotes" class="mt-1 text-amber-800">Allergies/Notes: {{ medicalNotes }}</p>
                </div>
              </div>
            </div>

            <!-- Date & Time, Doctor, Patient Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <p class="text-xs text-gray-500 mb-1">Consultation Schedule</p>
                <p class="font-medium text-sm flex items-center text-gray-900">
                  <LucideCalendar class="w-4 h-4 mr-1.5 text-primary-600" />
                  <span>{{ formatDateLong(selectedDate) }}</span>
                </p>
                <p class="font-medium text-sm flex items-center text-primary-700 mt-1 font-mono">
                  <LucideClock class="w-4 h-4 mr-1.5 text-primary-600" />
                  <span>{{ formatTime12h(selectedTime) }}</span>
                </p>
              </div>

              <div>
                <p class="text-xs text-gray-500 mb-1">Attending Doctor</p>
                <p class="font-medium text-sm flex items-center text-gray-900">
                  <LucideUser class="w-4 h-4 mr-1.5 text-teal-600" />
                  <span>Dr. {{ selectedDoctor?.user.name }}</span>
                </p>
                <p class="text-xs text-teal-700 font-semibold mt-0.5">
                  {{ selectedDoctor?.specialty?.name || 'General Specialist' }}
                </p>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <p class="text-xs text-gray-500 mb-1">Patient Name</p>
                <p class="font-medium text-sm text-gray-900">{{ patientForm.name }}</p>
                <p class="text-xs text-gray-500 font-mono">{{ patientForm.phone }}</p>
              </div>

              <div>
                <p class="text-xs text-gray-500 mb-1">Clinic Location</p>
                <p class="font-medium text-sm text-gray-900 flex items-start">
                  <LucideMapPin class="w-4 h-4 mr-1.5 mt-0.5 text-primary-600 shrink-0" />
                  <span>SMMG Healthcare Clinic – Consultation Dept.</span>
                </p>
              </div>
            </div>
          </div>

          <!-- poiseathome Shield Notice Banner -->
          <div class="flex items-start rounded-xl border border-teal-100 bg-teal-50/60 p-4 text-sm font-medium text-teal-900 mb-7">
            <LucideShieldCheck class="mr-3 mt-0.5 h-5 w-5 shrink-0 text-teal-600" />
            <p>
              By confirming, your appointment is submitted to the clinic registry in <strong>Pending</strong> status. Clinic staff will verify schedule and room availability and notify you.
            </p>
          </div>

          <!-- Bottom Navigation -->
          <div class="flex justify-between border-t border-gray-100 pt-5">
            <button type="button" class="btn btn-ghost" @click="step = 3">
              <LucideArrowLeft class="h-4 w-4 mr-1.5" /> Back
            </button>
            <button type="button" class="btn btn-primary" @click="handleStep4Continue">
              <span>Proceed to Confirm</span>
              <LucideArrowRight class="h-4 w-4 ml-1.5" />
            </button>
          </div>
        </div>

        <!-- ========================================================================= -->
        <!-- STEP 5: CONFIRM -->
        <!-- ========================================================================= -->
        <div v-if="step === 5" class="p-6 md:p-8 space-y-6">
          <div class="mb-6">
            <p class="text-xs font-bold uppercase tracking-[.15em] text-primary-600">Step 5 of 6</p>
            <h2 class="mt-2 text-2xl font-bold">Confirm Appointment</h2>
            <p class="mt-1 text-sm text-gray-500">Confirm and finalize your consultation reservation.</p>
          </div>

          <!-- Summary Confirmation Card -->
          <div class="rounded-2xl border border-teal-200 bg-gradient-to-br from-teal-50/50 via-white to-primary-50/40 p-6 space-y-4">
            <div class="flex items-center gap-3">
              <div class="h-10 w-10 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center font-bold">
                <LucideCheckCircle2 class="h-6 w-6" />
              </div>
              <div>
                <h3 class="font-bold text-gray-900 text-base">Confirm Consultation with Dr. {{ selectedDoctor?.user.name }}</h3>
                <p class="text-xs text-gray-600">
                  Scheduled for <strong>{{ formatDateLong(selectedDate) }}</strong> at <strong class="font-mono text-primary-700">{{ formatTime12h(selectedTime) }}</strong>
                </p>
              </div>
            </div>

            <!-- Agreement Checkbox -->
            <div class="pt-4 border-t border-teal-100">
              <label class="flex items-start gap-3 cursor-pointer select-none">
                <input
                  v-model="confirmAgreed"
                  type="checkbox"
                  class="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="text-xs text-gray-700 leading-relaxed">
                  I verify that the consultation details and symptoms provided are accurate. I commit to attend at the scheduled time or provide at least 24 hours notice for any rescheduling or cancellation.
                </span>
              </label>
            </div>
          </div>

          <!-- Bottom Navigation -->
          <div class="mt-8 flex justify-between border-t border-gray-100 pt-5">
            <button type="button" class="btn btn-ghost" :disabled="isSubmitting" @click="step = 4">
              <LucideArrowLeft class="h-4 w-4 mr-1.5" /> Back
            </button>
            <button
              type="button"
              class="btn btn-primary px-8 py-3"
              :disabled="!confirmAgreed || isSubmitting"
              @click="handleFinalBookingSubmit"
            >
              <LucideLoader2 v-if="isSubmitting" class="h-4 w-4 animate-spin mr-1.5" />
              <span>{{ isSubmitting ? 'Confirming...' : 'Confirm Appointment' }}</span>
              <LucideArrowRight v-if="!isSubmitting" class="h-4 w-4 ml-1.5" />
            </button>
          </div>
        </div>

        <!-- ========================================================================= -->
        <!-- STEP 6: PRINT APPOINTMENT DETAIL (Exact poiseathome success & slip) -->
        <!-- ========================================================================= -->
        <div v-if="step === 6 && createdAppointment" class="p-6 md:p-8 space-y-6">
          <!-- Success Hero (poiseathome Step 6 aesthetic) -->
          <div class="flex flex-col items-center justify-center p-6 text-center no-print">
            <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-100 text-teal-700 shadow-sm">
              <LucideCheckCircle2 class="h-8 w-8" />
            </div>
            <h2 class="text-2xl font-bold text-gray-900 mb-1">Appointment Request Submitted!</h2>
            <p class="text-sm text-gray-500 mb-2">
              Your appointment reference is <strong class="font-mono text-gray-900 text-base">{{ createdAppointment.appointment_reference }}</strong>.
            </p>
            <span class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200 mb-6">
              Status: Pending Clinic Verification
            </span>

            <!-- Action Buttons (poiseathome style) -->
            <div class="flex flex-wrap items-center justify-center gap-3 max-w-md w-full">
              <button
                type="button"
                class="btn btn-primary flex-1 justify-center py-3 flex items-center gap-2"
                @click="handlePrintSlip"
              >
                <LucidePrinter class="h-4 w-4" />
                <span>Print Appointment Detail</span>
              </button>

              <NuxtLink
                :to="`/patient/appointments/${createdAppointment.id}`"
                class="btn btn-secondary flex-1 justify-center py-3 flex items-center gap-2"
              >
                <LucideActivity class="h-4 w-4 text-teal-600" />
                <span>Track Live Progress</span>
              </NuxtLink>
            </div>
          </div>

          <!-- THE OFFICIAL PRINTABLE APPOINTMENT DETAIL SLIP -->
          <div class="printable-slip rounded-2xl border-2 border-teal-800 bg-white p-6 sm:p-8 space-y-6 shadow-sm">
            <!-- Header -->
            <div class="flex items-start justify-between border-b-2 border-teal-800 pb-5">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="h-6 w-6 rounded bg-teal-800 text-white font-bold flex items-center justify-center text-xs">S</span>
                  <h1 class="text-xl font-bold tracking-tight text-gray-900">SMMG HEALTHCARE CLINIC</h1>
                </div>
                <p class="text-xs text-gray-500 uppercase tracking-wider font-semibold">Official Consultation Pass & Appointment Slip</p>
                <p class="text-[11px] text-gray-500">St. Mary's Medical Group • Outpatient Department</p>
              </div>

              <div class="text-right space-y-1">
                <span class="inline-block px-2.5 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                  PENDING CONFIRMATION
                </span>
                <p class="text-xs text-gray-600 font-mono mt-1">Ref: <strong class="text-sm font-bold text-gray-900">{{ createdAppointment.appointment_reference }}</strong></p>
                <p class="text-[10px] text-gray-400">Date: {{ new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}</p>
              </div>
            </div>

            <!-- Two-Column Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
              <div class="space-y-2 border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                <h4 class="font-bold text-xs uppercase tracking-wider text-teal-800 border-b border-gray-200 pb-1.5 flex items-center gap-1.5">
                  <LucideUser class="h-3.5 w-3.5" />
                  <span>Patient Information</span>
                </h4>
                <div class="space-y-1 pt-1">
                  <p><span class="text-gray-500">Full Name:</span> <strong class="text-gray-900">{{ patientForm.name }}</strong></p>
                  <p><span class="text-gray-500">DOB / Gender:</span> <strong class="text-gray-900">{{ patientForm.date_of_birth }} ({{ patientForm.gender }})</strong></p>
                  <p><span class="text-gray-500">Phone:</span> <span class="font-mono text-gray-900">{{ patientForm.phone }}</span></p>
                  <p><span class="text-gray-500">Email:</span> <span class="text-gray-900">{{ patientForm.email }}</span></p>
                  <p><span class="text-gray-500">Address:</span> <span class="text-gray-900">{{ patientForm.address }}</span></p>
                  <p v-if="patientForm.emergency_contact_name"><span class="text-gray-500">Emergency Contact:</span> <span class="text-gray-900">{{ patientForm.emergency_contact_name }} ({{ patientForm.emergency_contact_phone }})</span></p>
                </div>
              </div>

              <div class="space-y-2 border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                <h4 class="font-bold text-xs uppercase tracking-wider text-teal-800 border-b border-gray-200 pb-1.5 flex items-center gap-1.5">
                  <LucideCalendar class="h-3.5 w-3.5" />
                  <span>Consultation Details</span>
                </h4>
                <div class="space-y-1 pt-1">
                  <p><span class="text-gray-500">Attending Doctor:</span> <strong class="text-gray-900">Dr. {{ selectedDoctor?.user.name }}</strong></p>
                  <p><span class="text-gray-500">Specialty:</span> <strong class="text-teal-700">{{ selectedDoctor?.specialty?.name || 'Medical Specialist' }}</strong></p>
                  <p><span class="text-gray-500">Service:</span> <strong class="text-gray-900">{{ selectedServiceName }}</strong></p>
                  <p><span class="text-gray-500">Date:</span> <strong class="text-gray-900">{{ formatDateLong(selectedDate) }}</strong></p>
                  <p><span class="text-gray-500">Time:</span> <strong class="text-primary-700 font-mono">{{ formatTime12h(selectedTime) }}</strong> (30 mins)</p>
                  <p><span class="text-gray-500">Location:</span> <span class="text-gray-900">SMMG Outpatient Clinic – Consultation Room 102</span></p>
                </div>
              </div>
            </div>

            <!-- Symptoms Section -->
            <div class="border border-gray-200 rounded-xl p-4 bg-gray-50/50 text-xs space-y-1">
              <h4 class="font-bold uppercase tracking-wider text-teal-800 border-b border-gray-200 pb-1.5 flex items-center gap-1.5">
                <LucideClipboardList class="h-3.5 w-3.5" />
                <span>Recorded Symptoms</span>
              </h4>
              <p class="pt-1"><span class="text-gray-500">Chief Complaint:</span> <span class="text-gray-900 font-medium">{{ symptoms }}</span></p>
              <p><span class="text-gray-500">Duration:</span> <span class="text-gray-900 font-medium">{{ symptomDuration }}</span></p>
              <p v-if="medicalNotes"><span class="text-gray-500">Notes / Allergies:</span> <span class="text-amber-800 font-medium">{{ medicalNotes }}</span></p>
            </div>

            <!-- Guidelines -->
            <div class="border-t border-dashed border-gray-300 pt-4 space-y-1.5 text-[11px] text-gray-600">
              <h5 class="font-bold text-gray-900 uppercase tracking-wider">Patient Guidelines:</h5>
              <ol class="list-decimal list-inside space-y-1">
                <li>Arrive at the clinic at least 15 minutes prior to your scheduled consultation.</li>
                <li>Present this appointment slip (digital or printed) at reception upon arrival.</li>
                <li>Bring a valid government-issued or student ID and any relevant medical records.</li>
              </ol>
            </div>

            <!-- Footer Line -->
            <div class="pt-5 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
              <div>
                <p>Official Record • SMMG Healthcare System</p>
                <p class="text-[10px] text-gray-400">ID: {{ createdAppointment.id }}</p>
              </div>
              <div class="border-t border-gray-300 pt-1 w-44 text-center">
                <span class="text-[10px] uppercase font-semibold text-gray-400">Authorized Signature</span>
              </div>
            </div>
          </div>

          <!-- Bottom Actions for Step 6 (Hidden when printing) -->
          <div class="flex justify-between border-t border-gray-100 pt-5 no-print">
            <NuxtLink to="/patient/appointments" class="btn btn-secondary flex items-center gap-1.5">
              <LucideCalendar class="h-4 w-4" />
              <span>All Appointments</span>
            </NuxtLink>
            <NuxtLink to="/patient/dashboard" class="btn btn-primary flex items-center gap-1.5">
              <LucideArrowRight class="h-4 w-4" />
              <span>Return to Dashboard</span>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
