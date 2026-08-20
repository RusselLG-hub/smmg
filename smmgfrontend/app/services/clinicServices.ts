import type { ClinicService, ServiceCreate, ServiceUpdate } from '~~/shared/types/ClinicService'

export const useClinicServicesService = () => {
  const { $api } = useNuxtApp()

  return {
    getServices: (activeOnly = false, specialtyId?: string) =>
      $api<ClinicService[]>('/v1/services', {
        params: {
          active_only: activeOnly,
          specialty_id: specialtyId,
        },
      }),

    getService: (id: string) =>
      $api<ClinicService>(`/v1/services/${id}`),

    createService: (data: ServiceCreate) =>
      $api<ClinicService>('/v1/services', {
        method: 'POST',
        body: data,
      }),

    updateService: (id: string, data: ServiceUpdate) =>
      $api<ClinicService>(`/v1/services/${id}`, {
        method: 'PUT',
        body: data,
      }),

    deleteService: (id: string) =>
      $api<void>(`/v1/services/${id}`, {
        method: 'DELETE',
      }),
  }
}
