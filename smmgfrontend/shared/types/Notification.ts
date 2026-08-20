export interface InAppNotification {
  id: string
  title: string
  message: string
  kind: 'appointment' | 'reminder' | 'status'
  created_at: string
  href: string
}

