import type {
  AdminDashboardSummary,
  DoctorDashboardSummary,
  PatientDashboardSummary,
  StaffDashboardSummary,
} from '~~/shared/types/Dashboard'

export const useDashboardService = () => {
  const { $api } = useNuxtApp()

  return {
    getPatientDashboard: () => $api<PatientDashboardSummary>('/v1/dashboard/patient'),
    getDoctorDashboard: () => $api<DoctorDashboardSummary>('/v1/dashboard/doctor'),
    getStaffDashboard: () => $api<StaffDashboardSummary>('/v1/dashboard/staff'),
    getAdminDashboard: () => $api<AdminDashboardSummary>('/v1/dashboard/admin'),
  }
}
