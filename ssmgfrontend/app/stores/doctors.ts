import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useDoctorsService } from '~/services/doctors'
import type { Doctor, DoctorCreate, DoctorUpdate } from '~~/shared/types/Doctor'

export const useDoctorsStore = defineStore('doctors', () => {
  const doctors = ref<Doctor[]>([])
  const currentDoctor = ref<Doctor | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const doctorsService = useDoctorsService()

  const fetchDoctors = async (activeOnly = false, specialtyId?: string) => {
    loading.value = true
    error.value = null
    try {
      doctors.value = await doctorsService.getDoctors(activeOnly, specialtyId)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctors'
    } finally {
      loading.value = false
    }
  }

  const fetchDoctor = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      currentDoctor.value = await doctorsService.getDoctor(id)
      return currentDoctor.value
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor detail'
    } finally {
      loading.value = false
    }
  }

  const createDoctor = async (data: DoctorCreate) => {
    loading.value = true
    error.value = null
    try {
      const created = await doctorsService.createDoctor(data)
      doctors.value.unshift(created)
      return created
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to create doctor'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateDoctor = async (id: string, data: DoctorUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updated = await doctorsService.updateDoctor(id, data)
      const index = doctors.value.findIndex(d => d.id === id)
      if (index !== -1) {
        doctors.value[index] = updated
      }
      if (currentDoctor.value?.id === id) {
        currentDoctor.value = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to update doctor'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteDoctor = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await doctorsService.deleteDoctor(id)
      doctors.value = doctors.value.filter(d => d.id !== id)
      if (currentDoctor.value?.id === id) {
        currentDoctor.value = null
      }
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to delete doctor'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    doctors,
    currentDoctor,
    loading,
    error,
    fetchDoctors,
    fetchDoctor,
    createDoctor,
    updateDoctor,
    deleteDoctor,
  }
})
