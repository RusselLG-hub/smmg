import type { PatientProfile, PatientProfileUpdate } from '~~/shared/types/Patient'

export const usePatientService = () => {
  const { $api } = useNuxtApp()

  return {
    getMyProfile: () =>
      $api<PatientProfile>('/v1/patients/me'),

    updateMyProfile: (data: PatientProfileUpdate) =>
      $api<PatientProfile>('/v1/patients/me', {
        method: 'PUT',
        body: data,
      }),
  }
}
