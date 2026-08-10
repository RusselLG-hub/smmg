import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useDashboardService } from '~/services/dashboard'
import type {
  AdminDashboardSummary,
  DoctorDashboardSummary,
  PatientDashboardSummary,
  StaffDashboardSummary,
} from '~~/shared/types/Dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const patientSummary = ref<PatientDashboardSummary | null>(null)
  const doctorSummary = ref<DoctorDashboardSummary | null>(null)
  const staffSummary = ref<StaffDashboardSummary | null>(null)
  const adminSummary = ref<AdminDashboardSummary | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const dashboardService = useDashboardService()

  const fetchPatientDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      patientSummary.value = await dashboardService.getPatientDashboard()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch patient dashboard summary'
    } finally {
      loading.value = false
    }
  }

  const fetchDoctorDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      doctorSummary.value = await dashboardService.getDoctorDashboard()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor dashboard summary'
    } finally {
      loading.value = false
    }
  }

  const fetchStaffDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      staffSummary.value = await dashboardService.getStaffDashboard()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch staff dashboard summary'
    } finally {
      loading.value = false
    }
  }

  const fetchAdminDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      adminSummary.value = await dashboardService.getAdminDashboard()
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch admin dashboard summary'
    } finally {
      loading.value = false
    }
  }

  return {
    patientSummary,
    doctorSummary,
    staffSummary,
    adminSummary,
    loading,
    error,
    fetchPatientDashboard,
    fetchDoctorDashboard,
    fetchStaffDashboard,
    fetchAdminDashboard,
  }
})
