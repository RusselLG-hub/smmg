import type {
  Appointment,
  AppointmentCancelRequest,
  AppointmentCreateRequest,
  AppointmentRescheduleRequest,
  AppointmentStatusUpdateRequest,
} from '~~/shared/types/Appointment'

export const useAppointmentsService = () => {
  const { $api } = useNuxtApp()

  return {
    createAppointment: (data: AppointmentCreateRequest) =>
      $api<Appointment>('/v1/appointments', {
        method: 'POST',
        body: data,
      }),

    getMyAppointments: (typeFilter: string = 'all') =>
      $api<Appointment[]>('/v1/appointments/me', {
        params: { type: typeFilter },
      }),

    getDoctorAppointments: (dateStr?: string, status?: string) =>
      $api<Appointment[]>('/v1/appointments/doctor/me', {
        params: { date: dateStr, status },
      }),

    getAdminAppointments: (filters?: {
      doctor_id?: string
      patient_id?: string
      status?: string
      date?: string
    }) =>
      $api<Appointment[]>('/v1/appointments', {
        params: filters,
      }),

    getAppointmentDetails: (id: string) =>
      $api<Appointment>(`/v1/appointments/${id}`),

    cancelAppointment: (id: string, reason?: string) =>
      $api<Appointment>(`/v1/appointments/${id}/cancel`, {
        method: 'PATCH',
        body: { cancellation_reason: reason } as AppointmentCancelRequest,
      }),

    rescheduleAppointment: (id: string, date: string, time: string) =>
      $api<Appointment>(`/v1/appointments/${id}/reschedule`, {
        method: 'PATCH',
        body: { date, time } as AppointmentRescheduleRequest,
      }),

    updateAppointmentStatus: (id: string, status: string) =>
      $api<Appointment>(`/v1/appointments/${id}/status`, {
        method: 'PATCH',
        body: { status } as AppointmentStatusUpdateRequest,
      }),
  }
}
