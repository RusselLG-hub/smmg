<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useDoctorsStore } from '~/stores/doctors'
import { useSchedulesStore } from '~/stores/schedules'
import { useClinicServicesStore } from '~/stores/clinicServices'
import { useAppointmentsStore } from '~/stores/appointments'
import { useAuthStore } from '~/stores/auth'

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
const selectedSlot = ref<string | null>(null)
const selectedServiceId = ref<string>('')
const reasonInput = ref('')

const showBookingModal = ref(false)
const bookingSuccess = ref<{ reference: string; date: string; time: string } | null>(null)
const bookingError = ref<string | null>(null)
const isSubmitting = ref(false)

onMounted(async () => {
  await Promise.all([
    doctorsStore.fetchDoctor(doctorId),
    clinicServicesStore.fetchServices(true),
  ])
  if (doctorsStore.currentDoctor) {
    await schedulesStore.fetchAvailability(doctorId, selectedDate.value)
  }
})

watch(selectedDate, async (newDate) => {
  if (newDate && doctorId) {
    selectedSlot.value = null
    await schedulesStore.fetchAvailability(doctorId, newDate)
  }
})

const handleInitiateBooking = () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  if (!selectedSlot.value) return
  bookingError.value = null
  showBookingModal.value = true
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
      <!-- Success Banner -->
      <div v-if="bookingSuccess" class="bg-green-50 border border-green-200 rounded-xl p-6 space-y-3">
        <div class="flex items-center gap-3 text-green-800">
          <LucideCheckCircle2 class="h-6 w-6 text-green-600 shrink-0" />
          <div>
            <h3 class="text-lg font-bold">Appointment Booked Successfully!</h3>
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
      <div class="card overflow-hidden">
        <div class="p-8 border-b border-gray-200 flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <div class="h-24 w-24 rounded-full overflow-hidden bg-primary-50 border-2 border-primary-200 flex items-center justify-center shrink-0">
            <img
              v-if="doctorsStore.currentDoctor.profile_image_url"
              :src="doctorsStore.currentDoctor.profile_image_url"
              :alt="doctorsStore.currentDoctor.user.name"
              class="h-full w-full object-cover"
            />
            <LucideStethoscope v-else class="h-12 w-12 text-primary-600" />
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
            <div v-if="clinicServicesStore.services.length > 0" class="w-full sm:w-48">
              <label class="form-label mb-1">Clinic Service</label>
              <select v-model="selectedServiceId" class="form-input w-full text-xs">
                <option value="">General Consultation</option>
                <option v-for="srv in clinicServicesStore.services" :key="srv.id" :value="srv.id">{{ srv.name }}</option>
              </select>
            </div>

            <!-- Date Selector -->
            <div class="w-full sm:w-44">
              <label class="form-label mb-1">Target Date</label>
              <input
                v-model="selectedDate"
                type="date"
                :min="todayStr"
                class="form-input w-full text-xs"
              />
            </div>
          </div>
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

            <div v-if="selectedSlot" class="pt-4 border-t border-gray-100 flex justify-end">
              <button
                class="btn btn-primary px-6 flex items-center gap-2"
                @click="handleInitiateBooking"
              >
                <LucideCalendarCheck class="h-4 w-4" />
                <span>Confirm Selection & Book ({{ selectedSlot }})</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- BOOKING CONFIRMATION MODAL -->
    <div v-if="showBookingModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Confirm appointment booking">
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
