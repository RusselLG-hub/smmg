import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useNotificationsService } from '~/services/notifications'
import type { InAppNotification } from '~~/shared/types/Notification'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<InAppNotification[]>([])
  const readIds = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentUserId = ref<string | null>(null)
  const service = useNotificationsService()

  const unreadCount = computed(() =>
    items.value.filter(item => !readIds.value.includes(item.id)).length,
  )

  const storageKey = (userId: string) => `ssmg:notification-reads:${userId}`

  const loadReadState = (userId: string) => {
    if (currentUserId.value !== userId) items.value = []
    currentUserId.value = userId
    if (!import.meta.client) return
    try {
      const value = sessionStorage.getItem(storageKey(userId))
      readIds.value = value ? JSON.parse(value) : []
    } catch {
      readIds.value = []
    }
  }

  const persistReadState = () => {
    if (!import.meta.client || !currentUserId.value) return
    sessionStorage.setItem(storageKey(currentUserId.value), JSON.stringify(readIds.value.slice(-100)))
  }

  const fetchNotifications = async (userId: string) => {
    if (currentUserId.value !== userId) loadReadState(userId)
    loading.value = true
    error.value = null
    try {
      items.value = await service.getNotifications()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Notifications are unavailable right now.'
    } finally {
      loading.value = false
    }
  }

  const markRead = (id: string) => {
    if (!readIds.value.includes(id)) readIds.value.push(id)
    persistReadState()
  }

  const markAllRead = () => {
    readIds.value = [...new Set([...readIds.value, ...items.value.map(item => item.id)])]
    persistReadState()
  }

  const reset = () => {
    items.value = []
    readIds.value = []
    currentUserId.value = null
    error.value = null
  }

  return { items, loading, error, unreadCount, readIds, fetchNotifications, markRead, markAllRead, reset }
})
