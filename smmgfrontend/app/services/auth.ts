import type {
  AuthResponse,
  ForgotPasswordRequest,
  LoginRequest,
  MessageResponse,
  PasswordChangeConfirmRequest,
  ProfileUpdateRequest,
  RegisterRequest,
  ResetPasswordRequest,
  ResendVerificationRequest,
  VerifyEmailRequest,
} from '~~/shared/types/Auth'
import type { User } from '~~/shared/types/User'

export const useAuthService = () => {
  const { $api } = useNuxtApp()

  return {
    register: (data: RegisterRequest) =>
      $api<AuthResponse>('/v1/auth/register', {
        method: 'POST',
        body: data,
      }),

    verifyEmail: (data: VerifyEmailRequest) =>
      $api<AuthResponse>('/v1/auth/verify-email', {
        method: 'POST',
        body: data,
      }),

    resendVerification: (data: ResendVerificationRequest) =>
      $api<MessageResponse>('/v1/auth/verify-email/resend', {
        method: 'POST',
        body: data,
      }),

    login: (data: LoginRequest) =>
      $api<AuthResponse>('/v1/auth/login', {
        method: 'POST',
        body: data,
      }),

    logout: () =>
      $api<MessageResponse>('/v1/auth/logout', {
        method: 'POST',
      }),

    getMe: () =>
      $api<User>('/v1/auth/me', {
        method: 'GET',
      }),

    updateMe: (data: ProfileUpdateRequest) =>
      $api<User>('/v1/auth/me', {
        method: 'PATCH',
        body: data,
      }),

    requestPasswordChange: () =>
      $api<MessageResponse>('/v1/auth/password-change/request', {
        method: 'POST',
      }),

    confirmPasswordChange: (data: PasswordChangeConfirmRequest) =>
      $api<MessageResponse>('/v1/auth/password-change/confirm', {
        method: 'POST',
        body: data,
      }),

    forgotPassword: (data: ForgotPasswordRequest) =>
      $api<MessageResponse>('/v1/auth/forgot-password', {
        method: 'POST',
        body: data,
      }),

    resetPassword: (data: ResetPasswordRequest) =>
      $api<MessageResponse>('/v1/auth/reset-password', {
        method: 'POST',
        body: data,
      }),
  }
}
