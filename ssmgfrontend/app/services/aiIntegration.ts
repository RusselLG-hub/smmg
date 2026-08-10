import type {
  AIChatMessage,
  AIChatSession,
  AIChatSessionDetail,
} from '~~/shared/types/AiIntegration'

export const useAiIntegrationService = () => {
  const { $api } = useNuxtApp()

  return {
    createSession: (title?: string) =>
      $api<AIChatSession>('/v1/ai-integration/sessions', {
        method: 'POST',
        body: title ? { title } : undefined,
      }),

    getSessions: () =>
      $api<AIChatSession[]>('/v1/ai-integration/sessions'),

    getSessionDetails: (sessionId: string) =>
      $api<AIChatSessionDetail>(`/v1/ai-integration/sessions/${sessionId}`),

    deleteSession: (sessionId: string) =>
      $api<void>(`/v1/ai-integration/sessions/${sessionId}`, {
        method: 'DELETE',
      }),

    sendMessage: (sessionId: string, content: string) =>
      $api<AIChatMessage>(`/v1/ai-integration/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: { content },
      }),
  }
}
