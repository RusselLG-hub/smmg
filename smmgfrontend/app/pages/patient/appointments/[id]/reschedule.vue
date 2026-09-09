<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useAppointmentsService } from '~/services/appointments'
import { useAppointmentsStore } from '~/stores/appointments'
import { useSchedulesStore } from '~/stores/schedules'
import type { Appointment } from '~~/shared/types/Appointment'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const appointmentId = String(route.params.id)
const appointmentsService = useAppointmentsService()
const appointmentsStore = useAppointmentsStore()
const schedulesStore = useSchedulesStore()
const appointment = ref<Appointment | null>(null)
const selectedDate = ref('')
const selectedSlot = ref<string | null>(null)
const loading = ref(true)
const saving = ref(false)
const errorMsg = ref<string | null>(null)
const successMsg = ref<string | null>(null)
const today = new Date().toISOString().split('T')[0]

onMounted(async () => {
  try {
    appointment.value = await appointmentsService.getAppointmentDetails(appointmentId)
    selectedDate.value = appointment.value.scheduled_at.split('T')[0]
    await schedulesStore.fetchAvailability(appointment.value.doctor_profile_id, selectedDate.value)
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to load appointment'
  } finally {
    loading.value = false
  }
})

watch(selectedDate, async (date, previousDate) => {
  if (!appointment.value || !date || date === previousDate) return
  selectedSlot.value = null
  await schedulesStore.fetchAvailability(appointment.value.doctor_profile_id, date)
})

const submitReschedule = async () => {
  if (!selectedSlot.value || appointment.value?.status !== 'pending') return
  saving.value = true
  errorMsg.value = null
  try {
    await appointmentsStore.rescheduleAppointment(appointmentId, selectedDate.value, selectedSlot.value)
    successMsg.value = 'Appointment rescheduled successfully.'
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to reschedule appointment.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-4 py-10 sm:px-6">
    <NuxtLink to="/patient/appointments" class="mb-5 inline-flex items-center gap-2 text-sm font-semibold text-primary-700"><LucideArrowLeft class="h-4 w-4" /> Back to appointments</NuxtLink>
    <section class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <header class="border-b border-gray-200 bg-gradient-to-r from-primary-50 via-white to-teal-50 px-6 py-6 sm:px-8">
        <p class="section-label">Patient appointment</p><h1 class="mt-1 text-2xl font-bold text-slate-950">Reschedule Appointment</h1><p class="mt-2 text-sm text-slate-600">Choose a new available date and time for your consultation.</p>
      </header>
      <div v-if="loading" class="flex justify-center py-20"><LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" /></div>
      <div v-else-if="appointment && appointment.status === 'confirmed'" class="p-6 sm:p-8 space-y-4">
        <div class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-800 flex items-start gap-3">
          <LucideAlertCircle class="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p class="font-semibold text-sm">Reschedule Not Permitted</p>
            <p class="text-xs mt-1 text-amber-700 leading-relaxed">
              This appointment ({{ appointment.appointment_reference }}) has already been confirmed. Confirmed appointments cannot be rescheduled online. Please contact clinic reception or staff to arrange any changes.
            </p>
          </div>
        </div>
        <div class="flex justify-start">
          <NuxtLink to="/patient/appointments" class="btn btn-secondary">
            <LucideArrowLeft class="h-4 w-4" />
            <span>Back to Appointments</span>
          </NuxtLink>
        </div>
      </div>
      <form v-else class="space-y-6 p-6 sm:p-8" @submit.prevent="submitReschedule">
        <BaseAlertBanner v-if="successMsg" type="success" :message="successMsg" @dismiss="successMsg = null" />
        <BaseAlertBanner v-if="errorMsg" type="error" :message="errorMsg" @dismiss="errorMsg = null" />
        <div v-if="appointment" class="rounded-xl border border-gray-200 bg-gray-50 p-5"><p class="text-xs font-medium text-gray-500">Appointment</p><p class="mt-1 font-semibold text-gray-900">Dr. {{ appointment.doctor.user.name }} · {{ appointment.appointment_reference }}</p></div>
        <div><label class="form-label">New Date</label><input v-model="selectedDate" type="date" :min="today" required class="form-input" /></div>
        <div>
          <label class="form-label">Available Time</label>
          <div v-if="schedulesStore.loading" class="py-10 text-center"><LucideLoader2 class="mx-auto h-6 w-6 animate-spin text-primary-600" /></div>
          <div v-else-if="!schedulesStore.availability?.slots.length" class="rounded-xl border border-gray-200 bg-gray-50 p-6 text-center text-sm text-gray-500">No available slots for this date.</div>
          <div v-else class="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <button v-for="slot in schedulesStore.availability.slots" :key="slot.start_time" type="button" class="rounded-lg border px-3 py-2.5 font-mono text-sm" :class="selectedSlot === slot.start_time ? 'border-primary-600 bg-primary-600 text-white' : 'border-gray-200 bg-white hover:border-primary-300 hover:bg-primary-50'" @click="selectedSlot = slot.start_time">{{ slot.start_time }} — {{ slot.end_time }}</button>
          </div>
        </div>
        <div class="flex flex-col-reverse gap-3 border-t border-gray-200 pt-6 sm:flex-row sm:justify-end"><NuxtLink to="/patient/appointments" class="btn btn-secondary justify-center">Cancel</NuxtLink><button type="submit" class="btn btn-primary justify-center" :disabled="saving || !selectedSlot"><LucideLoader2 v-if="saving" class="h-4 w-4 animate-spin" /><LucideSave v-else class="h-4 w-4" />{{ saving ? 'Saving...' : 'Save New Schedule' }}</button></div>
      </form>
    </section>
  </div>
</template>
