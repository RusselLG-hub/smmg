import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAppointmentsService } from '~/services/appointments'
import type {
  Appointment,
  AppointmentCreateRequest,
} from '~~/shared/types/Appointment'

export const useAppointmentsStore = defineStore('appointments', () => {
  const myAppointments = ref<Appointment[]>([])
  const doctorAppointments = ref<Appointment[]>([])
  const adminAppointments = ref<Appointment[]>([])
  const currentAppointment = ref<Appointment | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const appointmentsService = useAppointmentsService()

  const createAppointment = async (data: AppointmentCreateRequest) => {
    loading.value = true
    error.value = null
    try {
      const created = await appointmentsService.createAppointment(data)
      myAppointments.value.unshift(created)
      return created
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to book appointment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMyAppointments = async (typeFilter: string = 'all') => {
    loading.value = true
    error.value = null
    try {
      myAppointments.value = await appointmentsService.getMyAppointments(typeFilter)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch appointments'
    } finally {
      loading.value = false
    }
  }

  const fetchDoctorAppointments = async (dateStr?: string, status?: string) => {
    loading.value = true
    error.value = null
    try {
      doctorAppointments.value = await appointmentsService.getDoctorAppointments(dateStr, status)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor appointments'
    } finally {
      loading.value = false
    }
  }

  const fetchAdminAppointments = async (filters?: {
    doctor_id?: string
    patient_id?: string
    status?: string
    date?: string
  }) => {
    loading.value = true
    error.value = null
    try {
      adminAppointments.value = await appointmentsService.getAdminAppointments(filters)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch admin appointments'
    } finally {
      loading.value = false
    }
  }

  const fetchAppointmentDetails = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const details = await appointmentsService.getAppointmentDetails(id)
      currentAppointment.value = details
      _updateInStore(details)
      return details
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch appointment details'
      throw err
    } finally {
      loading.value = false
    }
  }

  const cancelAppointment = async (id: string, reason?: string) => {
    loading.value = true
    error.value = null
    try {
      const updated = await appointmentsService.cancelAppointment(id, reason)
      _updateInStore(updated)
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to cancel appointment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const rescheduleAppointment = async (id: string, date: string, time: string) => {
    loading.value = true
    error.value = null
    try {
      const updated = await appointmentsService.rescheduleAppointment(id, date, time)
      _updateInStore(updated)
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to reschedule appointment'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateStatus = async (id: string, status: string) => {
    loading.value = true
    error.value = null
    try {
      const updated = await appointmentsService.updateAppointmentStatus(id, status)
      _updateInStore(updated)
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to update appointment status'
      throw err
    } finally {
      loading.value = false
    }
  }

  const _updateInStore = (updated: Appointment) => {
    const idxMy = myAppointments.value.findIndex(a => a.id === updated.id)
    if (idxMy !== -1) myAppointments.value[idxMy] = updated

    const idxDoc = doctorAppointments.value.findIndex(a => a.id === updated.id)
    if (idxDoc !== -1) doctorAppointments.value[idxDoc] = updated

    const idxAdm = adminAppointments.value.findIndex(a => a.id === updated.id)
    if (idxAdm !== -1) adminAppointments.value[idxAdm] = updated

    if (currentAppointment.value?.id === updated.id) {
      currentAppointment.value = updated
    }
  }

  return {
    myAppointments,
    doctorAppointments,
    adminAppointments,
    currentAppointment,
    loading,
    error,
    createAppointment,
    fetchMyAppointments,
    fetchDoctorAppointments,
    fetchAdminAppointments,
    fetchAppointmentDetails,
    cancelAppointment,
    rescheduleAppointment,
    updateStatus,
  }
})
