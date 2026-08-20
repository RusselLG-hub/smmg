import type { InAppNotification } from '~~/shared/types/Notification'

export const useNotificationsService = () => {
  const { $api } = useNuxtApp()

  return {
    getNotifications: (limit = 12) =>
      $api<InAppNotification[]>('/v1/notifications', {
        query: { limit },
      }),
  }
}

