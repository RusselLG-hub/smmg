import type {
  AvailabilityResponse,
  DoctorSchedule,
  DoctorScheduleCreate,
  DoctorScheduleUpdate,
} from '~~/shared/types/Schedule'

export const useSchedulesService = () => {
  const { $api } = useNuxtApp()

  return {
    getDoctorSchedules: (doctorId: string) =>
      $api<DoctorSchedule[]>(`/v1/schedules/doctors/${doctorId}`),

    createSchedule: (data: DoctorScheduleCreate) =>
      $api<DoctorSchedule>('/v1/schedules', {
        method: 'POST',
        body: data,
      }),

    updateSchedule: (id: string, data: DoctorScheduleUpdate) =>
      $api<DoctorSchedule>(`/v1/schedules/${id}`, {
        method: 'PUT',
        body: data,
      }),

    deleteSchedule: (id: string) =>
      $api<void>(`/v1/schedules/${id}`, {
        method: 'DELETE',
      }),

    getDoctorAvailability: (doctorId: string, dateStr: string) =>
      $api<AvailabilityResponse>(`/v1/doctors/${doctorId}/availability`, {
        params: { date: dateStr },
      }),
  }
}
