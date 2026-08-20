import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useSchedulesService } from '~/services/schedules'
import type {
  AvailabilityResponse,
  DoctorSchedule,
  DoctorScheduleCreate,
  DoctorScheduleUpdate,
} from '~~/shared/types/Schedule'

export const useSchedulesStore = defineStore('schedules', () => {
  const schedules = ref<DoctorSchedule[]>([])
  const availability = ref<AvailabilityResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const schedulesService = useSchedulesService()

  const fetchDoctorSchedules = async (doctorId: string) => {
    loading.value = true
    error.value = null
    try {
      schedules.value = await schedulesService.getDoctorSchedules(doctorId)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor schedules'
    } finally {
      loading.value = false
    }
  }

  const fetchAllDoctorSchedules = async (doctorIds: string[]) => {
    loading.value = true
    error.value = null
    try {
      const results = await Promise.all(
        doctorIds.map(doctorId => schedulesService.getDoctorSchedules(doctorId)),
      )
      schedules.value = results.flat()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor schedules'
    } finally {
      loading.value = false
    }
  }

  const createSchedule = async (data: DoctorScheduleCreate) => {
    loading.value = true
    error.value = null
    try {
      const created = await schedulesService.createSchedule(data)
      schedules.value.push(created)
      return created
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to create schedule'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSchedule = async (id: string, data: DoctorScheduleUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updated = await schedulesService.updateSchedule(id, data)
      const index = schedules.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schedules.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to update schedule'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteSchedule = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await schedulesService.deleteSchedule(id)
      schedules.value = schedules.value.filter(s => s.id !== id)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to delete schedule'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAvailability = async (doctorId: string, dateStr: string) => {
    loading.value = true
    error.value = null
    try {
      availability.value = await schedulesService.getDoctorAvailability(doctorId, dateStr)
      return availability.value
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor availability'
    } finally {
      loading.value = false
    }
  }

  return {
    schedules,
    availability,
    loading,
    error,
    fetchDoctorSchedules,
    fetchAllDoctorSchedules,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    fetchAvailability,
  }
})
