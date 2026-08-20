import type {
  DoctorPersonalReportResponse,
  ReportsOverviewResponse,
} from '~~/shared/types/Report'

export const useReportsService = () => {
  const { $api } = useNuxtApp()

  return {
    getReportsOverview: (startDate?: string, endDate?: string) =>
      $api<ReportsOverviewResponse>('/v1/reports/overview', {
        params: {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        },
      }),

    getDoctorPersonalReport: (startDate?: string, endDate?: string) =>
      $api<DoctorPersonalReportResponse>('/v1/reports/doctor/me', {
        params: {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        },
      }),
  }
}
