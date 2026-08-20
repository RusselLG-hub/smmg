<script setup lang="ts">
import { Bell, BellOff, Check, LoaderCircle } from '@lucide/vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useNotificationsStore } from '~/stores/notifications'

const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()
const open = ref(false)
const root = ref<HTMLElement | null>(null)

const hasItems = computed(() => notificationsStore.items.length > 0)
const isUnread = (id: string) => !notificationsStore.readIds.includes(id)

const refresh = async () => {
  if (authStore.user?.id) await notificationsStore.fetchNotifications(authStore.user.id)
}

const toggle = async () => {
  open.value = !open.value
  if (open.value) await refresh()
}

const openItem = (id: string) => {
  notificationsStore.markRead(id)
  open.value = false
}

const formatRelativeTime = (value: string) => {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 1000))
  if (seconds < 60) return 'Just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return days < 7 ? `${days}d ago` : new Intl.DateTimeFormat('en-PH', { month: 'short', day: 'numeric' }).format(new Date(value))
}

const handleDocumentClick = (event: MouseEvent) => {
  if (open.value && root.value && !root.value.contains(event.target as Node)) open.value = false
}
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') open.value = false
}

onMounted(() => {
  refresh()
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleKeydown)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="relative flex h-11 w-11 items-center justify-center rounded-xl border border-gray-200 bg-white text-gray-600 transition hover:border-primary-200 hover:bg-primary-50 hover:text-primary-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
      :aria-expanded="open"
      aria-haspopup="dialog"
      aria-label="Open notifications"
      @click="toggle"
    >
      <Bell class="h-5 w-5" aria-hidden="true" />
      <span
        v-if="notificationsStore.unreadCount"
        class="absolute -right-1 -top-1 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white ring-2 ring-white"
      >{{ notificationsStore.unreadCount > 9 ? '9+' : notificationsStore.unreadCount }}</span>
    </button>

    <div
      v-if="open"
      role="dialog"
      aria-label="Notifications"
      class="fixed inset-x-3 top-[4.5rem] z-50 max-h-[calc(100dvh-5.5rem)] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl sm:absolute sm:inset-auto sm:right-0 sm:top-14 sm:w-[24rem]"
    >
      <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
        <div>
          <h2 class="text-sm font-bold text-gray-900">Notifications</h2>
          <p class="text-xs text-gray-500">Recent appointment activity</p>
        </div>
        <button
          v-if="notificationsStore.unreadCount"
          type="button"
          class="flex min-h-10 items-center gap-1.5 rounded-lg px-2 text-xs font-semibold text-primary-700 hover:bg-primary-50"
          @click="notificationsStore.markAllRead"
        >
          <Check class="h-4 w-4" /> Mark all read
        </button>
      </div>

      <div class="max-h-[calc(100dvh-10.5rem)] overflow-y-auto sm:max-h-[28rem]">
        <div v-if="notificationsStore.loading" class="flex items-center justify-center gap-2 px-4 py-10 text-sm text-gray-500">
          <LoaderCircle class="h-5 w-5 animate-spin text-primary-600" /> Loading updates…
        </div>
        <div v-else-if="notificationsStore.error" class="px-5 py-8 text-center">
          <p class="text-sm text-red-700">{{ notificationsStore.error }}</p>
          <button type="button" class="mt-3 min-h-10 text-sm font-semibold text-primary-700 hover:underline" @click="refresh">Try again</button>
        </div>
        <div v-else-if="!hasItems" class="px-5 py-10 text-center">
          <BellOff class="mx-auto h-7 w-7 text-gray-400" />
          <p class="mt-2 text-sm font-semibold text-gray-700">No appointment updates</p>
          <p class="mt-1 text-xs text-gray-500">New activity will appear here.</p>
        </div>
        <NuxtLink
          v-for="item in notificationsStore.items"
          v-else
          :key="item.id"
          :to="item.href"
          class="flex gap-3 border-b border-gray-100 px-4 py-3.5 transition last:border-0 hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary-500"
          @click="openItem(item.id)"
        >
          <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full" :class="isUnread(item.id) ? 'bg-primary-600' : 'bg-gray-300'" />
          <span class="min-w-0">
            <span class="block text-sm font-semibold text-gray-900">{{ item.title }}</span>
            <span class="mt-0.5 block text-xs leading-5 text-gray-600">{{ item.message }}</span>
            <span class="mt-1 block text-[11px] font-medium text-gray-400">{{ formatRelativeTime(item.created_at) }}</span>
          </span>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

