import type { User } from './User'

export interface RegisterRequest {
  email: string
  name: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface VerifyEmailRequest {
  email: string
  code: string
}

export interface ResendVerificationRequest {
  email: string
}

export interface ProfileUpdateRequest {
  name?: string
  profile_image_url?: string | null
}

export interface PasswordChangeConfirmRequest {
  code: string
  new_password: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  email: string
  code: string
  new_password: string
}

export interface AuthResponse {
  user: User
  message: string
}

export interface MessageResponse {
  message: string
}
