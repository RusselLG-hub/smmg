export interface DoctorSchedule {
  id: string
  doctor_profile_id: string
  day_of_week: number // 0=Monday, 6=Sunday
  start_time: string // HH:MM
  end_time: string // HH:MM
  slot_duration_minutes: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface DoctorScheduleCreate {
  doctor_profile_id?: string | null
  day_of_week: number
  start_time: string
  end_time: string
  slot_duration_minutes?: number
  is_active?: boolean
}

export interface DoctorScheduleUpdate {
  day_of_week?: number
  start_time?: string
  end_time?: string
  slot_duration_minutes?: number
  is_active?: boolean
}

export interface TimeSlot {
  start_time: string
  end_time: string
  is_available: boolean
}

export interface AvailabilityResponse {
  doctor_id: string
  date: string
  day_of_week: number
  is_working_day: boolean
  slots: TimeSlot[]
}

export interface MonthlyAvailabilityResponse {
  doctor_id: string
  year: number
  month: number
  days: AvailabilityResponse[]
}

export const WEEKDAYS = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
]
