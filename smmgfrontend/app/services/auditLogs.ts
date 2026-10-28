export interface AuditLogItem {
  id: string
  user_id?: string | null
  user_name?: string | null
  user_role?: string | null
  action: string
  description: string
  auditable_type?: string | null
  auditable_id?: string | null
  properties?: Record<string, any> | null
  ip_address?: string | null
  user_agent?: string | null
  created_at: string
}

export interface AuditLogListResponse {
  logs: AuditLogItem[]
  pagination: {
    current_page: number
    last_page: number
    per_page: number
    total: number
  }
  stats: {
    total_logs: number
    today_logs: number
    actions_count: Record<string, number>
  }
}

export const useAuditLogService = () => {
  const { $api } = useNuxtApp()

  return {
    getLogs: (params: {
      page?: number
      per_page?: number
      action?: string
      role?: string
      search?: string
    }) =>
      $api<AuditLogListResponse>('/v1/audit-logs', {
        params,
      }),
  }
}
