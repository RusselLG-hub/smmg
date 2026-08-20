export interface StatusBreakdown {
  pending_count: number
  confirmed_count: number
  completed_count: number
  cancelled_count: number
  total_count: number
  completion_rate_pct: number
  cancellation_rate_pct: number
}

export interface VolumePoint {
  date: string
  count: number
}

export interface DoctorReportRow {
  doctor_profile_id: string
  doctor_name: string
  specialty_name?: string | null
  total_appointments: number
  completed_appointments: number
  cancelled_appointments: number
  pending_appointments: number
  confirmed_appointments: number
  completion_rate_pct: number
}

export interface ServiceUsageRow {
  service_id?: string | null
  service_name: string
  specialty_name?: string | null
  appointment_count: number
  completed_count: number
  cancelled_count: number
  percentage_of_total: number
}

export interface SpecialtyReportRow {
  specialty_id: string
  specialty_name: string
  doctor_count: number
  appointment_count: number
  service_count: number
}

export interface PeakTimeRow {
  label: string
  count: number
}

export interface PeakBookingTimes {
  busiest_days: PeakTimeRow[]
  busiest_hours: PeakTimeRow[]
}

export interface DemographicGroup {
  label: string
  count: number
}

export interface PatientDemographicSummary {
  gender_distribution: DemographicGroup[]
  age_distribution: DemographicGroup[]
  total_patients: number
}

export interface ReportsOverviewResponse {
  start_date: string
  end_date: string
  status_breakdown: StatusBreakdown
  volume_trend: VolumePoint[]
  doctor_stats: DoctorReportRow[]
  service_stats: ServiceUsageRow[]
  specialty_stats: SpecialtyReportRow[]
  peak_times: PeakBookingTimes
  demographics: PatientDemographicSummary
}

export interface DoctorPersonalReportResponse {
  doctor_name: string
  specialty_name?: string | null
  start_date: string
  end_date: string
  status_breakdown: StatusBreakdown
  volume_trend: VolumePoint[]
  service_stats: ServiceUsageRow[]
  peak_times: PeakBookingTimes
}
