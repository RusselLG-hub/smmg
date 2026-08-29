<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useAiIntegrationStore } from '~/stores/aiIntegration'
import { usePatientService } from '~/services/patient'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const aiStore = useAiIntegrationStore()
const patientService = usePatientService()
const profileImageUrl = useState<string | null>('patient-profile-image-url', () => null)

const inputMessage = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const sidebarOpen = ref(false)
const pendingDeleteId = ref<string | null>(null)
const deletingChat = ref(false)
const hasActiveChat = computed(() => Boolean(aiStore.activeSessionId && aiStore.activeSession))
const suggestedQuestions = [
  'What should I do for a minor burn?',
  'How do I properly clean a small cut?',
  'When should a fever be checked by a doctor?',
  'What are warning signs of a medical emergency?',
]
const healthTips = [
  'Drink water regularly, especially during hot weather or physical activity.',
  'Wash hands with soap for at least 20 seconds to reduce the spread of infection.',
  'Seek urgent care for severe chest pain, trouble breathing, heavy bleeding, or loss of consciousness.',
]

onMounted(async () => {
  if (authStore.user?.role === 'patient' && !profileImageUrl.value) {
    try {
      const profile = await patientService.getMyProfile()
      profileImageUrl.value = profile.profile_image_url || null
    } catch {}
  }

  await aiStore.fetchSessions()
  if (aiStore.sessions.length === 0) {
    await aiStore.createNewSession()
  }
  scrollToBottom()
})

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

watch(
  () => aiStore.activeSession?.messages.length,
  () => {
    scrollToBottom()
  }
)

const handleSendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text || aiStore.sending || !hasActiveChat.value) return
  inputMessage.value = ''
  await aiStore.sendMessage(text)
  scrollToBottom()
}

const handleSuggestedQuestion = async (question: string) => {
  if (aiStore.sending || !hasActiveChat.value) return
  inputMessage.value = question
  await handleSendMessage()
}

const handleCreateNewChat = async () => {
  await aiStore.createNewSession()
  sidebarOpen.value = false
}

const requestDeleteChat = (id: string) => {
  pendingDeleteId.value = id
}

const handleDeleteChat = async () => {
  if (!pendingDeleteId.value) return
  deletingChat.value = true
  try {
    await aiStore.deleteSession(pendingDeleteId.value)
    pendingDeleteId.value = null
    if (!aiStore.activeSessionId) inputMessage.value = ''
  } finally {
    deletingChat.value = false
  }
}

const formatDate = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatMessageContent = (content: string) => {
  return content
    .replace(/\*\*/g, '')
    .replace(/__/g, '')
    .replace(/^\s*#{1,6}\s+/gm, '')
    .replace(/^\s*[*+]\s+/gm, '- ')
    .replace(/```/g, '')
    .replace(/`/g, '')
    .trim()
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-5rem)] flex flex-col">
    <!-- Disclaimer Banners -->
    <div class="bg-amber-50 border border-amber-200 text-amber-900 px-4 py-2.5 rounded-xl text-xs flex items-center justify-between mb-4 shrink-0">
      <div class="flex items-center gap-2">
        <LucideAlertTriangle class="h-4 w-4 text-amber-600 shrink-0" />
        <span>
          <strong>Notice:</strong> Provides general health education and basic first-aid guidance. Does not replace professional medical diagnosis or care.
        </span>
      </div>

      <div class="hidden sm:flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-100 px-2.5 py-1 rounded-md">
        <LucidePhoneCall class="h-3.5 w-3.5" />
        <span>Philippine emergencies: Call 911</span>
      </div>
    </div>

    <!-- Main Chat Workspace Layout -->
    <div class="flex-1 bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex relative">
      <!-- Mobile Sidebar Toggle Overlay -->
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 bg-black/30 z-20 md:hidden"
        @click="sidebarOpen = false"
      ></div>

      <!-- Chat Sessions Sidebar -->
      <aside
        class="w-72 bg-gray-50 border-r border-gray-200 flex flex-col z-30 transition-transform duration-200 absolute md:static inset-y-0 left-0"
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      >
        <div class="p-4 border-b border-gray-200 flex items-center justify-between">
          <button
            class="w-full flex items-center justify-center gap-2 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors"
            @click="handleCreateNewChat"
          >
            <LucidePlus class="h-4 w-4" />
            <span>New Consultation Chat</span>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-3 space-y-1">
          <div v-if="aiStore.sessions.length === 0" class="py-8 text-center text-xs text-gray-500">
            No previous chat sessions.
          </div>

          <div
            v-for="s in aiStore.sessions"
            :key="s.id"
            class="group flex items-center justify-between p-3 rounded-xl cursor-pointer text-xs transition-colors"
            :class="s.id === aiStore.activeSessionId ? 'bg-primary-100 text-primary-900 font-bold' : 'text-gray-700 hover:bg-gray-100'"
            @click="aiStore.selectSession(s.id); sidebarOpen = false"
          >
            <div class="flex items-center gap-2 truncate">
              <LucideMessageSquare class="h-4 w-4 shrink-0 text-primary-600" />
              <span class="truncate">{{ s.title || 'Consultation Chat' }}</span>
            </div>

            <button
              class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600 p-1 rounded transition-opacity"
              title="Delete session"
              @click.stop="requestDeleteChat(s.id)"
            >
              <LucideTrash2 class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </aside>

      <!-- Active Conversation Area -->
      <main class="flex-1 flex flex-col h-full bg-white relative">
        <!-- Chat Header Bar -->
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white shrink-0">
          <div class="flex items-center gap-3">
            <button
              class="md:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              @click="sidebarOpen = !sidebarOpen"
            >
              <LucideMenu class="h-5 w-5" />
            </button>

            <div class="h-9 w-9 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center">
              <LucideBot class="h-5 w-5" />
            </div>

            <div>
              <h2 class="text-sm font-bold text-gray-900">
                {{ aiStore.activeSession?.title || 'AI Health & First-Aid Assistant' }}
              </h2>
              <p class="text-xs text-gray-500">General Health & Emergency First-Aid Assistant</p>
            </div>
          </div>

          <button
            v-if="aiStore.activeSessionId"
            class="text-xs text-red-600 hover:text-red-800 font-semibold flex items-center gap-1"
            @click="requestDeleteChat(aiStore.activeSessionId)"
          >
            <LucideTrash2 class="h-3.5 w-3.5" />
            <span>Delete Chat</span>
          </button>
        </div>

        <!-- Chat Messages Container -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
          <div v-if="aiStore.loading" class="flex justify-center py-12">
            <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
          </div>

          <template v-else-if="aiStore.activeSession?.messages">
            <!-- Initial Welcome Message if empty session -->
            <div v-if="aiStore.activeSession.messages.length === 0" class="py-8 text-center space-y-3 max-w-2xl mx-auto">
              <div class="h-12 w-12 rounded-2xl bg-teal-100 text-teal-700 flex items-center justify-center mx-auto">
                <LucideStethoscope class="h-6 w-6" />
              </div>
              <h3 class="text-base font-bold text-gray-900">How can I assist your health today?</h3>
              <p class="text-xs text-gray-500">
                Ask about basic first-aid procedures, general symptom information, or wellness advice.
              </p>
              <div class="grid gap-2 pt-3 sm:grid-cols-2">
                <button
                  v-for="question in suggestedQuestions"
                  :key="question"
                  type="button"
                  class="rounded-xl border border-teal-200 bg-teal-50 px-3 py-2.5 text-left text-xs font-medium text-teal-800 transition-colors hover:border-teal-300 hover:bg-teal-100"
                  @click="handleSuggestedQuestion(question)"
                >
                  {{ question }}
                </button>
              </div>
              <div class="pt-5 text-left">
                <div class="mb-2 flex items-center justify-center gap-2 text-xs font-bold uppercase tracking-wide text-teal-700"><LucideHeartPulse class="h-4 w-4" />Quick Health Tips</div>
                <div class="grid gap-2 sm:grid-cols-3">
                  <div v-for="tip in healthTips" :key="tip" class="rounded-xl border border-gray-200 bg-gray-50 p-3 text-xs leading-5 text-gray-700">{{ tip }}</div>
                </div>
                <p class="mt-2 text-center text-[10px] text-gray-500">General education only. Consult a healthcare professional for personal medical advice.</p>
              </div>
            </div>

            <!-- Message List -->
            <div
              v-for="msg in aiStore.activeSession.messages"
              :key="msg.id"
              class="flex gap-4"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <!-- AI Avatar -->
              <div v-if="msg.role === 'assistant'" class="h-8 w-8 rounded-full bg-teal-600 text-white flex items-center justify-center shrink-0 mt-1">
                <LucideBot class="h-4 w-4" />
              </div>

              <div
                class="max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-1 shadow-sm"
                :class="
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white rounded-br-none font-medium'
                    : 'bg-gray-100 text-gray-900 rounded-bl-none border border-gray-200'
                "
              >
                <div class="whitespace-pre-wrap">{{ formatMessageContent(msg.content) }}</div>
                <div
                  class="text-[10px] text-right font-mono mt-1"
                  :class="msg.role === 'user' ? 'text-primary-200' : 'text-gray-600'"
                >
                  {{ formatDate(msg.created_at) }}
                </div>
              </div>

              <!-- User Avatar -->
              <div
                v-if="msg.role === 'user'"
                class="h-8 w-8 rounded-full overflow-hidden bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs shrink-0 mt-1 ring-1 ring-primary-200"
              >
                <BaseAvatar :src="profileImageUrl" :alt="authStore.user?.name || 'User'" />
              </div>
            </div>

            <!-- Generating Loading Indicator -->
            <div v-if="aiStore.sending" class="flex items-center gap-3">
              <div class="h-8 w-8 rounded-full bg-teal-600 text-white flex items-center justify-center shrink-0">
                <LucideBot class="h-4 w-4" />
              </div>
              <div class="bg-gray-100 border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-none text-xs text-gray-500 flex items-center gap-2">
                <LucideLoader2 class="h-4 w-4 text-teal-600 animate-spin" />
                <span>Assistant is evaluating your prompt...</span>
              </div>
            </div>
          </template>

          <div v-else class="flex h-full items-center justify-center py-12">
            <div class="max-w-sm text-center">
              <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
                <LucideMessageSquarePlus class="h-6 w-6" />
              </div>
              <h3 class="mt-4 text-base font-bold text-gray-900">Create a chat first</h3>
              <p class="mt-2 text-xs leading-5 text-gray-500">
                Add a new consultation chat before sending a message to the health assistant.
              </p>
              <button
                type="button"
                :disabled="aiStore.loading"
                class="btn btn-primary mt-5 px-5 py-2.5"
                @click="handleCreateNewChat"
              >
                <LucidePlus class="h-4 w-4" />
                <span>Create new chat</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Input Box Bar -->
        <div class="p-4 border-t border-gray-200 bg-white shrink-0">
          <form class="flex items-center gap-3" @submit.prevent="handleSendMessage">
            <input
              v-model="inputMessage"
              type="text"
              :placeholder="hasActiveChat ? 'Ask about general health information or basic first-aid...' : 'Create a chat before sending a message'"
              :disabled="aiStore.sending || !hasActiveChat"
              class="flex-1 px-4 py-3 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none disabled:bg-gray-50 text-gray-900"
            />

            <button
              type="submit"
              :disabled="!inputMessage.trim() || aiStore.sending || !hasActiveChat"
              class="px-5 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white rounded-xl text-xs font-semibold transition-colors shadow-sm flex items-center gap-1.5"
            >
              <LucideSend class="h-4 w-4" />
              <span>Send</span>
            </button>
          </form>
        </div>
      </main>
    </div>

    <BaseConfirmModal
      :model-value="Boolean(pendingDeleteId)"
      title="Delete chat session?"
      description="This conversation and its message history will be permanently removed."
      confirm-label="Delete Chat"
      :loading="deletingChat"
      @update:model-value="!$event && (pendingDeleteId = null)"
      @confirm="handleDeleteChat"
    />
  </div>
</template>
