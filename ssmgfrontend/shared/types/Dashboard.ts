import type { Appointment } from './Appointment'

export interface PatientDashboardSummary {
  upcoming_appointment?: Appointment | null
  upcoming_count: number
  completed_count: number
}

export interface DoctorDashboardSummary {
  today_count: number
  upcoming_count: number
  today_appointments: Appointment[]
  schedule_count: number
}

export interface StaffDashboardSummary {
  today_count: number
  pending_count: number
  confirmed_count: number
  completed_count: number
  cancelled_count: number
  today_appointments: Appointment[]
}

export interface AdminDashboardSummary {
  total_users: number
  total_patients: number
  total_doctors: number
  total_staff: number
  active_doctors_count: number
  today_appointments_count: number
  pending_count: number
  confirmed_count: number
  completed_count: number
  cancelled_count: number
  total_specialties: number
  total_services: number
}
