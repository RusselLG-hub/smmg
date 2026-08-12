import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAiIntegrationService } from '~/services/aiIntegration'
import type { AIChatSession, AIChatSessionDetail } from '~~/shared/types/AiIntegration'

export const useAiIntegrationStore = defineStore('aiIntegration', () => {
  const sessions = ref<AIChatSession[]>([])
  const activeSessionId = ref<string | null>(null)
  const activeSession = ref<AIChatSessionDetail | null>(null)
  const loading = ref(false)
  const sending = ref(false)
  const error = ref<string | null>(null)

  const aiService = useAiIntegrationService()

  const fetchSessions = async () => {
    loading.value = true
    error.value = null
    try {
      sessions.value = await aiService.getSessions()
      const firstSession = sessions.value.at(0)
      if (firstSession && !activeSessionId.value) {
        await selectSession(firstSession.id)
      }
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch AI chat sessions'
    } finally {
      loading.value = false
    }
  }

  const selectSession = async (sessionId: string) => {
    activeSessionId.value = sessionId
    loading.value = true
    error.value = null
    try {
      activeSession.value = await aiService.getSessionDetails(sessionId)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to load chat history'
    } finally {
      loading.value = false
    }
  }

  const createNewSession = async (title?: string) => {
    loading.value = true
    error.value = null
    try {
      const newSess = await aiService.createSession(title)
      sessions.value.unshift(newSess)
      await selectSession(newSess.id)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to create chat session'
    } finally {
      loading.value = false
    }
  }

  const deleteSession = async (sessionId: string) => {
    error.value = null
    try {
      await aiService.deleteSession(sessionId)
      sessions.value = sessions.value.filter((s) => s.id !== sessionId)
      if (activeSessionId.value === sessionId) {
        const firstSession = sessions.value.at(0)
        if (firstSession) {
          await selectSession(firstSession.id)
        } else {
          activeSessionId.value = null
          activeSession.value = null
        }
      }
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to delete chat session'
    }
  }

  const sendMessage = async (content: string) => {
    if (!activeSessionId.value || !activeSession.value) {
      error.value = 'Create a chat before sending a message'
      return
    }
    sending.value = true
    error.value = null

    const tempUserMsg = {
      id: 'temp-' + Date.now(),
      session_id: activeSessionId.value,
      role: 'user' as const,
      content,
      created_at: new Date().toISOString(),
    }
    if (activeSession.value) {
      activeSession.value.messages.push(tempUserMsg)
    }

    try {
      await aiService.sendMessage(activeSessionId.value, content)
      if (activeSession.value) {
        await selectSession(activeSessionId.value)
      }
      await fetchSessions()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to send AI message'
      if (activeSession.value) {
        activeSession.value.messages = activeSession.value.messages.filter((m) => m.id !== tempUserMsg.id)
      }
    } finally {
      sending.value = false
    }
  }

  return {
    sessions,
    activeSessionId,
    activeSession,
    loading,
    sending,
    error,
    fetchSessions,
    selectSession,
    createNewSession,
    deleteSession,
    sendMessage,
  }
})
