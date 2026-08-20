import type { User } from '~~/shared/types/User'
import type { RegisterRequest } from '~~/shared/types/Auth'

export const useUsersService = () => {
  const { $api } = useNuxtApp()

  return {
    getUsers: (role?: string) =>
      $api<User[]>('/v1/users', {
        params: role ? { role } : undefined,
      }),

    createStaffUser: (data: RegisterRequest) =>
      $api<User>('/v1/users/staff', {
        method: 'POST',
        body: data,
      }),

    toggleUserActive: (userId: string) =>
      $api<User>(`/v1/users/${userId}/toggle-active`, {
        method: 'PATCH',
      }),
  }
}
