import type { Specialty } from './Specialty'

export interface ClinicService {
  id: string
  name: string
  description?: string | null
  specialty_id?: string | null
  image_url?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  specialty?: Specialty | null
}

export interface ServiceCreate {
  name: string
  description?: string | null
  specialty_id?: string | null
  image_url?: string | null
  is_active?: boolean
}

export interface ServiceUpdate {
  name?: string
  description?: string | null
  specialty_id?: string | null
  image_url?: string | null
  is_active?: boolean
}
