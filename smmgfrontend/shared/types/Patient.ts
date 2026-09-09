import type { User } from './User'

export interface PatientDoctorSummary {
  id: string
  name: string
  title?: string | null
  specialty_name?: string | null
}

export interface PatientProfile {
  id: string
  user_id: string
  date_of_birth?: string | null
  gender?: string | null
  phone?: string | null
  address?: string | null
  profile_image_url?: string | null
  created_at: string
  updated_at: string
  user: User
  doctor?: PatientDoctorSummary | null
  appointment_status?: string | null
  appointment_reference?: string | null
  all_statuses?: string[]
}

export interface PatientProfileUpdate {
  name?: string
  date_of_birth?: string | null
  gender?: string | null
  phone?: string | null
  address?: string | null
  profile_image_url?: string | null
}
