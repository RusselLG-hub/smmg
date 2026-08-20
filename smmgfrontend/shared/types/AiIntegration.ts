export interface AIChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface AIChatSession {
  id: string
  user_id: string
  title?: string | null
  created_at: string
  updated_at: string
}

export interface AIChatSessionDetail extends AIChatSession {
  messages: AIChatMessage[]
}

export interface AIChatAdminSession extends AIChatSession {
  user: import('./User').User
  message_count: number
}

export interface AIChatAdminSessionDetail extends AIChatSessionDetail {
  user: import('./User').User
}

export interface CreateMessageRequest {
  content: string
}
