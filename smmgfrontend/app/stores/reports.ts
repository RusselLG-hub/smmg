import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useReportsService } from '~/services/reports'
import type {
  DoctorPersonalReportResponse,
  ReportsOverviewResponse,
} from '~~/shared/types/Report'

export const useReportsStore = defineStore('reports', () => {
  const startDate = ref<string>('')
  const endDate = ref<string>('')
  const overview = ref<ReportsOverviewResponse | null>(null)
  const doctorPersonal = ref<DoctorPersonalReportResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const reportsService = useReportsService()

  const fetchOverview = async (sDate?: string, eDate?: string) => {
    loading.value = true
    error.value = null
    try {
      if (sDate) startDate.value = sDate
      if (eDate) endDate.value = eDate
      overview.value = await reportsService.getReportsOverview(
        startDate.value || undefined,
        endDate.value || undefined
      )
      if (overview.value) {
        startDate.value = overview.value.start_date
        endDate.value = overview.value.end_date
      }
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch reports overview'
    } finally {
      loading.value = false
    }
  }

  const fetchDoctorPersonal = async (sDate?: string, eDate?: string) => {
    loading.value = true
    error.value = null
    try {
      if (sDate) startDate.value = sDate
      if (eDate) endDate.value = eDate
      doctorPersonal.value = await reportsService.getDoctorPersonalReport(
        startDate.value || undefined,
        endDate.value || undefined
      )
      if (doctorPersonal.value) {
        startDate.value = doctorPersonal.value.start_date
        endDate.value = doctorPersonal.value.end_date
      }
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch doctor report'
    } finally {
      loading.value = false
    }
  }

  return {
    startDate,
    endDate,
    overview,
    doctorPersonal,
    loading,
    error,
    fetchOverview,
    fetchDoctorPersonal,
  }
})
