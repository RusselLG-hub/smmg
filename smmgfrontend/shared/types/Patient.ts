import type { User } from './User'

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
}

export interface PatientProfileUpdate {
  name?: string
  date_of_birth?: string | null
  gender?: string | null
  phone?: string | null
  address?: string | null
  profile_image_url?: string | null
}
