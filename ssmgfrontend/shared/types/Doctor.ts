import type { Specialty } from './Specialty'
import type { User } from './User'

export interface Doctor {
  id: string
  user_id: string
  specialty_id?: string | null
  title?: string | null
  phone?: string | null
  bio?: string | null
  profile_image_url?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  user: User
  specialty?: Specialty | null
}

export interface DoctorCreate {
  email: string
  name: string
  password: string
  specialty_id?: string | null
  title?: string | null
  phone?: string | null
  bio?: string | null
  profile_image_url?: string | null
  is_active?: boolean
}

export interface DoctorUpdate {
  name?: string
  specialty_id?: string | null
  title?: string | null
  phone?: string | null
  bio?: string | null
  profile_image_url?: string | null
  is_active?: boolean
}
