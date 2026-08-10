import type {
  AuthResponse,
  LoginRequest,
  MessageResponse,
  RegisterRequest,
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
  }
}
