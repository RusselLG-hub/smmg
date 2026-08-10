import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useClinicServicesService } from '~/services/clinicServices'
import type { ClinicService, ServiceCreate, ServiceUpdate } from '~~/shared/types/ClinicService'

export const useClinicServicesStore = defineStore('clinicServices', () => {
  const services = ref<ClinicService[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const clinicServicesService = useClinicServicesService()

  const fetchServices = async (activeOnly = false, specialtyId?: string) => {
    loading.value = true
    error.value = null
    try {
      services.value = await clinicServicesService.getServices(activeOnly, specialtyId)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch services'
    } finally {
      loading.value = false
    }
  }

  const createService = async (data: ServiceCreate) => {
    loading.value = true
    error.value = null
    try {
      const created = await clinicServicesService.createService(data)
      services.value.push(created)
      return created
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to create service'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateService = async (id: string, data: ServiceUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updated = await clinicServicesService.updateService(id, data)
      const index = services.value.findIndex(s => s.id === id)
      if (index !== -1) {
        services.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to update service'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteService = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await clinicServicesService.deleteService(id)
      services.value = services.value.filter(s => s.id !== id)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to delete service'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    services,
    loading,
    error,
    fetchServices,
    createService,
    updateService,
    deleteService,
  }
})
