import type { Doctor, DoctorCreate, DoctorUpdate } from '~~/shared/types/Doctor'

export const useDoctorsService = () => {
  const { $api } = useNuxtApp()

  return {
    getDoctors: (activeOnly = false, specialtyId?: string) =>
      $api<Doctor[]>('/v1/doctors', {
        params: {
          active_only: activeOnly,
          specialty_id: specialtyId,
        },
      }),

    getDoctor: (id: string) =>
      $api<Doctor>(`/v1/doctors/${id}`),

    createDoctor: (data: DoctorCreate) =>
      $api<Doctor>('/v1/doctors', {
        method: 'POST',
        body: data,
      }),

    updateDoctor: (id: string, data: DoctorUpdate) =>
      $api<Doctor>(`/v1/doctors/${id}`, {
        method: 'PUT',
        body: data,
      }),

    deleteDoctor: (id: string) =>
      $api<void>(`/v1/doctors/${id}`, {
        method: 'DELETE',
      }),
  }
}
