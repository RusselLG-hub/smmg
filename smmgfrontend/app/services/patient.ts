import type { PatientProfile, PatientProfileUpdate } from '~~/shared/types/Patient'

export const usePatientService = () => {
  const { $api } = useNuxtApp()

  return {
    getPatientRecords: () =>
      $api<PatientProfile[]>('/v1/patients'),

    getMyProfile: () =>
      $api<PatientProfile>('/v1/patients/me'),

    updateMyProfile: (data: PatientProfileUpdate) =>
      $api<PatientProfile>('/v1/patients/me', {
        method: 'PUT',
        body: data,
      }),

    archivePatient: (patientId: string) =>
      $api<PatientProfile>(`/v1/patients/${patientId}/archive`, {
        method: 'PATCH',
      }),

    restorePatient: (patientId: string) =>
      $api<PatientProfile>(`/v1/patients/${patientId}/restore`, {
        method: 'PATCH',
      }),

    deletePatient: (patientId: string) =>
      $api<void>(`/v1/patients/${patientId}`, {
        method: 'DELETE',
      }),
  }
}
