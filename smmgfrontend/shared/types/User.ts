export type UserRole = 'patient' | 'doctor' | 'staff' | 'admin'

export interface User {
  id: string
  email: string
  name: string
  profile_image_url?: string | null
  role: UserRole
  is_active: boolean
  is_email_verified: boolean
  created_at: string
  updated_at: string
}
