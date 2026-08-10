import type { Doctor } from './Doctor'
import type { PatientProfile } from './Patient'
import type { ClinicService } from './ClinicService'

export type AppointmentStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed'

export interface Appointment {
  id: string
  appointment_reference: string
  patient_profile_id: string
  doctor_profile_id: string
  service_id?: string | null
  scheduled_at: string
  slot_duration_minutes: number
  status: AppointmentStatus
  reason?: string | null
  cancellation_reason?: string | null
  created_at: string
  updated_at: string
  patient: PatientProfile
  doctor: Doctor
  service?: ClinicService | null
}

export interface AppointmentCreateRequest {
  doctor_profile_id: string
  service_id?: string | null
  date: string // YYYY-MM-DD
  time: string // HH:MM
  reason?: string | null
}

export interface AppointmentRescheduleRequest {
  date: string // YYYY-MM-DD
  time: string // HH:MM
}

export interface AppointmentCancelRequest {
  cancellation_reason?: string | null
}

export interface AppointmentStatusUpdateRequest {
  status: AppointmentStatus
}
