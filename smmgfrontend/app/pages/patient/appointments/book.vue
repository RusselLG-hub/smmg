<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAppointmentsStore } from '~/stores/appointments'
import { useDoctorsStore } from '~/stores/doctors'
import { useClinicServicesStore } from '~/stores/clinicServices'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
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
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to complete booking. Please select another time if this slot is no longer available.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <NuxtLink :to="doctorId ? `/doctors/${doctorId}` : '/doctors'" class="mb-5 inline-flex items-center gap-2 text-sm font-semibold text-primary-700">
      <LucideArrowLeft class="h-4 w-4" /> Back to doctor
    </NuxtLink>
    <section class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <header class="border-b border-gray-200 bg-gradient-to-r from-primary-50 via-white to-teal-50 px-6 py-6 sm:px-8">
        <p class="section-label">Patient appointment</p>
        <h1 class="mt-1 text-2xl font-bold text-slate-950">Confirm Appointment Booking</h1>
        <p class="mt-2 text-sm text-slate-600">Review your appointment and optionally tell the clinic why you are visiting.</p>
      </header>
      <div v-if="loading" class="flex justify-center py-20"><LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" /></div>
      <div v-else-if="bookedReference" class="space-y-5 p-6 sm:p-8">
        <BaseAlertBanner type="success" :dismissible="false" :message="`Appointment request submitted for clinic confirmation. Reference: ${bookedReference}`" />
        <NuxtLink to="/patient/appointments" class="btn btn-primary">View My Appointments</NuxtLink>
      </div>
      <form v-else class="space-y-6 p-6 sm:p-8" @submit.prevent="submitBooking">
        <BaseAlertBanner v-if="errorMsg" type="error" :message="errorMsg" @dismiss="errorMsg = null" />
        <div class="grid gap-4 rounded-xl border border-gray-200 bg-gray-50 p-5 sm:grid-cols-2">
          <div><p class="text-xs font-medium text-gray-500">Doctor</p><p class="mt-1 font-semibold text-gray-900">Dr. {{ doctorsStore.currentDoctor?.user.name || 'Unavailable' }}</p></div>
          <div><p class="text-xs font-medium text-gray-500">Service</p><p class="mt-1 font-semibold text-gray-900">{{ serviceName }}</p></div>
          <div><p class="text-xs font-medium text-gray-500">Date</p><p class="mt-1 font-semibold text-gray-900">{{ date }}</p></div>
          <div><p class="text-xs font-medium text-gray-500">Time</p><p class="mt-1 font-mono font-semibold text-gray-900">{{ time }}</p></div>
        </div>
        <div><label class="form-label">Reason for Visit / Symptoms <span class="font-normal text-gray-500">(optional)</span></label><textarea v-model="reason" rows="5" maxlength="1000" class="form-input" placeholder="Briefly describe your concern..." /></div>
        <div class="flex flex-col-reverse gap-3 border-t border-gray-200 pt-6 sm:flex-row sm:justify-end">
          <NuxtLink :to="`/doctors/${doctorId}`" class="btn btn-secondary justify-center">Cancel</NuxtLink>
          <button type="submit" class="btn btn-primary justify-center" :disabled="saving || !doctorsStore.currentDoctor"><LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" /><LucideCalendarCheck v-else class="h-4 w-4" />{{ saving ? 'Booking...' : 'Complete Booking' }}</button>
        </div>
      </form>
    </section>
  </div>
</template>
