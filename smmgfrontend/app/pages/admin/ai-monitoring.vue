<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAiIntegrationService } from '~/services/aiIntegration'
import type { AIChatAdminSession, AIChatAdminSessionDetail } from '~~/shared/types/AiIntegration'

definePageMeta({ middleware: 'auth' })

const aiService = useAiIntegrationService()
const sessions = ref<AIChatAdminSession[]>([])
const selectedSession = ref<AIChatAdminSessionDetail | null>(null)
const search = ref('')
const loading = ref(true)
const loadingConversation = ref(false)
const errorMsg = ref<string | null>(null)

const filteredSessions = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return sessions.value
  return sessions.value.filter((session) =>
    [session.title, session.user.name, session.user.email, session.user.role]
      .some((value) => value?.toLowerCase().includes(query)),
  )
})

const formatDate = (value: string) => new Date(value).toLocaleString(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
})

const loadSessions = async () => {
  loading.value = true
  errorMsg.value = null
  try {
    sessions.value = await aiService.getAdminSessions()
    if (sessions.value[0]) await selectSession(sessions.value[0].id)
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to load AI conversations'
  } finally {
    loading.value = false
  }
}

const selectSession = async (sessionId: string) => {
  loadingConversation.value = true
  errorMsg.value = null
  try {
    selectedSession.value = await aiService.getAdminSessionDetails(sessionId)
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to load conversation messages'
  } finally {
    loadingConversation.value = false
  }
}

onMounted(loadSessions)
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-6 px-4 py-10 sm:px-6 lg:px-8">
    <BasePageHeader
      title="AI Conversation Monitoring"
      description="Review AI assistant conversations across all user accounts"
    />

    <div class="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      <LucideShieldAlert class="mt-0.5 h-5 w-5 shrink-0" />
      <p>Conversations may contain private health information. Access them only for authorized safety review and system monitoring.</p>
    </div>

    <div v-if="errorMsg" class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{{ errorMsg }}</div>

    <div v-if="loading" class="flex justify-center py-20">
      <LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" />
    </div>

    <div v-else class="grid min-h-[650px] overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm lg:grid-cols-[360px_1fr]">
      <aside class="border-b border-gray-200 lg:border-b-0 lg:border-r">
        <div class="border-b border-gray-200 p-4">
          <label for="conversation-search" class="sr-only">Search conversations</label>
          <div class="relative">
            <LucideSearch class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input id="conversation-search" v-model="search" type="search" class="form-input pl-9" placeholder="Search user, email, or title" />
          </div>
          <p class="mt-2 text-xs text-gray-500">{{ filteredSessions.length }} of {{ sessions.length }} conversations</p>
        </div>

        <div class="max-h-[560px] overflow-y-auto">
          <button
            v-for="session in filteredSessions"
            :key="session.id"
            type="button"
            class="w-full border-b border-gray-100 p-4 text-left transition-colors hover:bg-gray-50"
            :class="selectedSession?.id === session.id ? 'bg-primary-50' : 'bg-white'"
            @click="selectSession(session.id)"
          >
            <div class="flex items-start gap-3">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary-100 text-xs font-bold text-primary-700">
                <BaseAvatar :src="session.user.profile_image_url" :alt="`${session.user.name} avatar`" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-gray-900">{{ session.title || 'Untitled conversation' }}</p>
                <p class="truncate text-xs text-gray-600">{{ session.user.name }} · {{ session.user.email }}</p>
                <div class="mt-1 flex items-center justify-between text-xs text-gray-400">
                  <span class="capitalize">{{ session.user.role }}</span>
                  <span>{{ session.message_count }} messages</span>
                </div>
              </div>
            </div>
          </button>

          <div v-if="filteredSessions.length === 0" class="px-4 py-12 text-center text-sm text-gray-500">No conversations found.</div>
        </div>
      </aside>

      <section class="flex min-w-0 flex-col bg-gray-50/60">
        <div v-if="selectedSession" class="border-b border-gray-200 bg-white px-5 py-4">
          <h2 class="font-bold text-gray-900">{{ selectedSession.title || 'Untitled conversation' }}</h2>
          <p class="mt-1 text-xs text-gray-500">
            {{ selectedSession.user.name }} ({{ selectedSession.user.email }}) · Updated {{ formatDate(selectedSession.updated_at) }}
          </p>
        </div>

        <div v-if="loadingConversation" class="flex flex-1 items-center justify-center py-20">
          <LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" />
        </div>

        <div v-else-if="selectedSession" class="flex-1 space-y-4 overflow-y-auto p-5 sm:p-7">
          <article
            v-for="message in selectedSession.messages"
            :key="message.id"
            class="flex"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] rounded-2xl px-4 py-3 shadow-sm"
              :class="message.role === 'user' ? 'bg-primary-600 text-white' : 'border border-gray-200 bg-white text-gray-800'"
            >
              <div class="mb-1 flex items-center gap-2 text-xs font-semibold" :class="message.role === 'user' ? 'text-primary-100' : 'text-teal-700'">
                <LucideUser v-if="message.role === 'user'" class="h-3.5 w-3.5" />
                <LucideBot v-else class="h-3.5 w-3.5" />
                <span>{{ message.role === 'user' ? selectedSession.user.name : 'AI Assistant' }}</span>
              </div>
              <p class="whitespace-pre-wrap break-words text-sm leading-relaxed">{{ message.content }}</p>
              <p class="mt-2 text-right text-[11px]" :class="message.role === 'user' ? 'text-primary-200' : 'text-gray-400'">{{ formatDate(message.created_at) }}</p>
            </div>
          </article>

          <div v-if="selectedSession.messages.length === 0" class="py-20 text-center text-sm text-gray-500">This conversation has no messages.</div>
        </div>

        <div v-else class="flex flex-1 flex-col items-center justify-center px-6 py-20 text-center text-gray-500">
          <LucideMessagesSquare class="mb-3 h-10 w-10 text-gray-300" />
          <p class="font-medium text-gray-700">Select a conversation</p>
          <p class="mt-1 text-sm">Choose a session from the list to review its messages.</p>
        </div>
      </section>
    </div>
  </div>
</template>
