import type { Specialty, SpecialtyCreate, SpecialtyUpdate } from '~~/shared/types/Specialty'

export const useSpecialtiesService = () => {
  const { $api } = useNuxtApp()

  return {
    getSpecialties: (activeOnly = false) =>
      $api<Specialty[]>('/v1/specialties', {
        params: { active_only: activeOnly },
      }),

    getSpecialty: (id: string) =>
      $api<Specialty>(`/v1/specialties/${id}`),

    createSpecialty: (data: SpecialtyCreate) =>
      $api<Specialty>('/v1/specialties', {
        method: 'POST',
        body: data,
      }),

    updateSpecialty: (id: string, data: SpecialtyUpdate) =>
      $api<Specialty>(`/v1/specialties/${id}`, {
        method: 'PUT',
        body: data,
      }),

    deleteSpecialty: (id: string) =>
      $api<void>(`/v1/specialties/${id}`, {
        method: 'DELETE',
      }),
  }
}
