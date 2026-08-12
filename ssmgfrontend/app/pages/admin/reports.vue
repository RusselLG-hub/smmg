<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useReportsStore } from '~/stores/reports'

definePageMeta({
  middleware: 'auth',
})

const reportsStore = useReportsStore()

const activeTab = ref<'volume' | 'doctors' | 'services' | 'peaks_demo'>('volume')
const customStartDate = ref('')
const customEndDate = ref('')

onMounted(async () => {
  await reportsStore.fetchOverview()
  if (reportsStore.overview) {
    customStartDate.value = reportsStore.overview.start_date
    customEndDate.value = reportsStore.overview.end_date
  }
})

const handleApplyFilter = async () => {
  await reportsStore.fetchOverview(customStartDate.value, customEndDate.value)
}

const setPreset = async (days: number) => {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - days)

  customStartDate.value = start.toISOString().split('T')[0]
  customEndDate.value = end.toISOString().split('T')[0]
  await handleApplyFilter()
}

const maxVolumeCount = computed(() => {
  if (!reportsStore.overview?.volume_trend || reportsStore.overview.volume_trend.length === 0) return 1
  return Math.max(...reportsStore.overview.volume_trend.map((v) => v.count), 1)
})

// Simple CSV export
const exportDoctorCsv = () => {
  if (!reportsStore.overview?.doctor_stats) return
  const headers = ['Doctor', 'Specialty', 'Total Appts', 'Completed', 'Cancelled', 'Pending', 'Confirmed', 'Completion Rate %']
  const rows = reportsStore.overview.doctor_stats.map((d) => [
    `"${d.doctor_name}"`,
    `"${d.specialty_name || 'N/A'}"`,
    d.total_appointments,
    d.completed_appointments,
    d.cancelled_appointments,
    d.pending_appointments,
    d.confirmed_appointments,
    `${d.completion_rate_pct}%`,
  ])

  const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `doctor_reports_${customStartDate.value}_to_${customEndDate.value}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    <!-- Header Banner -->
    <div class="bg-gradient-to-r from-blue-900 to-teal-800 rounded-2xl p-5 sm:p-8 text-white shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-5">
      <div class="min-w-0">
        <span class="inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-semibold uppercase tracking-wider mb-2 backdrop-blur-sm">
          Operational Analytics & BI
        </span>
        <h1 class="text-2xl font-bold tracking-tight sm:text-3xl">Clinic Reports & Analytics</h1>
        <p class="text-blue-100 text-sm mt-1">Data insights on appointment volume, doctor performance, and service utilization</p>
      </div>

      <div class="flex w-full items-center gap-3 md:w-auto">
        <button
          class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-semibold text-blue-900 shadow transition-colors hover:bg-blue-50 md:w-auto"
          @click="exportDoctorCsv"
        >
          <LucideDownload class="h-4 w-4 text-blue-700" />
          <span>Export Doctor Stats CSV</span>
        </button>
      </div>
    </div>

    <!-- Date Filter Controls -->
    <div class="card p-5 space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-2 text-sm font-bold text-gray-900">
          <LucideFilter class="h-4 w-4 text-primary-600" />
          <span>Report Date Range Filter</span>
        </div>

        <!-- Quick Presets -->
        <div class="flex w-full flex-wrap items-center gap-2 sm:w-auto">
          <span class="w-full text-xs font-medium text-gray-500 sm:w-auto">Presets:</span>
          <button
            class="px-2.5 py-1 text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 rounded transition-colors"
            @click="setPreset(7)"
          >
            Last 7 Days
          </button>
          <button
            class="px-2.5 py-1 text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 rounded transition-colors"
            @click="setPreset(30)"
          >
            Last 30 Days
          </button>
          <button
            class="px-2.5 py-1 text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 rounded transition-colors"
            @click="setPreset(90)"
          >
            Last 90 Days
          </button>
        </div>
      </div>

      <form class="flex flex-col sm:flex-row items-end gap-4" @submit.prevent="handleApplyFilter">
        <div class="w-full sm:w-auto">
          <label class="form-label mb-1">Start Date</label>
          <input
            v-model="customStartDate"
            type="date"
            required
            class="form-input w-full text-xs"
          />
        </div>

        <div class="w-full sm:w-auto">
          <label class="form-label mb-1">End Date</label>
          <input
            v-model="customEndDate"
            type="date"
            required
            class="form-input w-full text-xs"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary w-full sm:w-auto text-xs"
        >
          Apply Date Filter
        </button>
      </form>
    </div>

    <!-- Loading State -->
    <div v-if="reportsStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <div v-else-if="reportsStore.overview" class="space-y-8">
      <!-- Executive Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <BaseStatCard
          label="Total Appointments"
          :value="reportsStore.overview.status_breakdown.total_count"
          variant="info"
        >
          <template #icon>
            <LucideCalendarCheck class="h-6 w-6 text-blue-600" />
          </template>
        </BaseStatCard>

        <BaseStatCard
          label="Completion Rate"
          :value="`${reportsStore.overview.status_breakdown.completion_rate_pct}%`"
          variant="success"
        >
          <template #icon>
            <LucideCheckCircle2 class="h-6 w-6 text-green-600" />
          </template>
        </BaseStatCard>

        <BaseStatCard
          label="Cancellation Rate"
          :value="`${reportsStore.overview.status_breakdown.cancellation_rate_pct}%`"
          variant="danger"
        >
          <template #icon>
            <LucideXCircle class="h-6 w-6 text-red-600" />
          </template>
        </BaseStatCard>

        <BaseStatCard
          label="Total Patient Base"
          :value="reportsStore.overview.demographics.total_patients"
          variant="default"
        >
          <template #icon>
            <LucideUsers class="h-6 w-6 text-teal-600" />
          </template>
        </BaseStatCard>
      </div>

      <!-- Navigation Tabs -->
      <div class="-mx-4 overflow-x-auto border-b border-gray-200 px-4 sm:mx-0 sm:px-0">
        <div class="flex min-w-max gap-1 sm:gap-3">
        <button
          class="flex shrink-0 items-center gap-2 border-b-2 px-3 py-3 text-sm font-semibold transition-colors sm:px-4"
          :class="activeTab === 'volume' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
          @click="activeTab = 'volume'"
        >
          <LucideBarChart3 class="h-4 w-4" />
          <span>Volume & Status</span>
        </button>

        <button
          class="flex shrink-0 items-center gap-2 border-b-2 px-3 py-3 text-sm font-semibold transition-colors sm:px-4"
          :class="activeTab === 'doctors' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
          @click="activeTab = 'doctors'"
        >
          <LucideStethoscope class="h-4 w-4" />
          <span>Doctor Performance</span>
        </button>

        <button
          class="flex shrink-0 items-center gap-2 border-b-2 px-3 py-3 text-sm font-semibold transition-colors sm:px-4"
          :class="activeTab === 'services' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
          @click="activeTab = 'services'"
        >
          <LucideHeartHandshake class="h-4 w-4" />
          <span>Services & Specialties</span>
        </button>

        <button
          class="flex shrink-0 items-center gap-2 border-b-2 px-3 py-3 text-sm font-semibold transition-colors sm:px-4"
          :class="activeTab === 'peaks_demo' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
          @click="activeTab = 'peaks_demo'"
        >
          <LucideClock class="h-4 w-4" />
          <span>Peak Times & Demographics</span>
        </button>
        </div>
      </div>

      <!-- TAB 1: VOLUME & STATUS -->
      <div v-if="activeTab === 'volume'" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Status Breakdown Progress -->
        <div class="card min-w-0 space-y-4 p-4 sm:p-6">
          <h2 class="text-base font-bold text-gray-900">Appointment Status Breakdown</h2>

          <div class="space-y-4 pt-2">
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1 text-gray-700">
                <span>Completed</span>
                <span>{{ reportsStore.overview.status_breakdown.completed_count }} ({{ reportsStore.overview.status_breakdown.completion_rate_pct }}%)</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div class="bg-green-600 h-3 rounded-full" :style="{ width: `${reportsStore.overview.status_breakdown.completion_rate_pct}%` }"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1 text-gray-700">
                <span>Confirmed</span>
                <span>{{ reportsStore.overview.status_breakdown.confirmed_count }}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div class="bg-blue-600 h-3 rounded-full" :style="{ width: `${reportsStore.overview.status_breakdown.total_count ? (reportsStore.overview.status_breakdown.confirmed_count / reportsStore.overview.status_breakdown.total_count * 100) : 0}%` }"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1 text-gray-700">
                <span>Pending</span>
                <span>{{ reportsStore.overview.status_breakdown.pending_count }}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div class="bg-yellow-500 h-3 rounded-full" :style="{ width: `${reportsStore.overview.status_breakdown.total_count ? (reportsStore.overview.status_breakdown.pending_count / reportsStore.overview.status_breakdown.total_count * 100) : 0}%` }"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1 text-gray-700">
                <span>Cancelled</span>
                <span>{{ reportsStore.overview.status_breakdown.cancelled_count }} ({{ reportsStore.overview.status_breakdown.cancellation_rate_pct }}%)</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div class="bg-red-600 h-3 rounded-full" :style="{ width: `${reportsStore.overview.status_breakdown.cancellation_rate_pct}%` }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Daily Volume CSS Chart -->
        <div class="card min-w-0 space-y-4 p-4 sm:p-6 lg:col-span-2">
          <h2 class="text-base font-bold text-gray-900">Daily Appointment Volume Trend</h2>

          <div v-if="reportsStore.overview.volume_trend.length === 0" class="py-12 text-center text-xs text-gray-500">
            No appointment volume data for this date range.
          </div>

          <div v-else class="h-72 overflow-x-auto pb-4">
            <div class="flex h-64 min-w-[640px] items-end gap-2 pt-6">
            <div
              v-for="v in reportsStore.overview.volume_trend"
              :key="v.date"
              class="flex-1 min-w-[28px] flex flex-col items-center gap-2 h-full justify-end group relative"
            >
              <div class="text-[10px] font-bold text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                {{ v.count }}
              </div>
              <div
                class="w-full bg-primary-500 hover:bg-primary-600 rounded-t-md transition-all"
                :style="{ height: `${(v.count / maxVolumeCount) * 80}%` }"
              ></div>
              <div class="mt-1 whitespace-nowrap font-mono text-[9px] text-gray-400">
                {{ v.date.substring(5) }}
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: DOCTOR PERFORMANCE -->
      <div v-if="activeTab === 'doctors'" class="card min-w-0 space-y-4 p-4 sm:p-6">
        <div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <h2 class="text-base font-bold text-gray-900">Doctor Utilization & Appointment Summary</h2>
          <span class="text-xs text-gray-500">{{ reportsStore.overview.doctor_stats.length }} Active Doctors</span>
        </div>

        <div class="-mx-4 overflow-x-auto sm:mx-0">
          <table class="min-w-[760px] w-full text-left text-sm text-gray-700">
            <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
              <tr>
                <th class="px-4 py-3">Doctor</th>
                <th class="px-4 py-3">Specialty</th>
                <th class="px-4 py-3 text-center">Total Appts</th>
                <th class="px-4 py-3 text-center">Completed</th>
                <th class="px-4 py-3 text-center">Cancelled</th>
                <th class="px-4 py-3 text-center">Completion Rate</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="d in reportsStore.overview.doctor_stats" :key="d.doctor_profile_id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-semibold text-gray-900">Dr. {{ d.doctor_name }}</td>
                <td class="px-4 py-3">
                  <span v-if="d.specialty_name" class="px-2 py-0.5 rounded text-xs font-medium bg-teal-50 text-teal-700">
                    {{ d.specialty_name }}
                  </span>
                  <span v-else class="text-xs text-gray-400">Unassigned</span>
                </td>
                <td class="px-4 py-3 text-center font-bold text-gray-900">{{ d.total_appointments }}</td>
                <td class="px-4 py-3 text-center text-green-700 font-semibold">{{ d.completed_appointments }}</td>
                <td class="px-4 py-3 text-center text-red-600">{{ d.cancelled_appointments }}</td>
                <td class="px-4 py-3 text-center font-bold text-primary-700">{{ d.completion_rate_pct }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB 3: SERVICES & SPECIALTIES -->
      <div v-if="activeTab === 'services'" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Service Usage -->
        <div class="card min-w-0 space-y-4 p-4 sm:p-6">
          <h2 class="text-base font-bold text-gray-900">Clinic Service Usage Breakdown</h2>
          <div class="overflow-x-auto">
            <table class="min-w-[420px] w-full text-left text-sm text-gray-700">
              <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
                <tr>
                  <th class="px-3 py-2">Service</th>
                  <th class="px-3 py-2 text-center">Appts</th>
                  <th class="px-3 py-2 text-center">% Share</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="srv in reportsStore.overview.service_stats" :key="srv.service_name" class="hover:bg-gray-50">
                  <td class="px-3 py-2">
                    <div class="font-semibold text-gray-900">{{ srv.service_name }}</div>
                    <div v-if="srv.specialty_name" class="text-xs text-gray-500">{{ srv.specialty_name }}</div>
                  </td>
                  <td class="px-3 py-2 text-center font-bold">{{ srv.appointment_count }}</td>
                  <td class="px-3 py-2 text-center font-medium text-teal-700">{{ srv.percentage_of_total }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Specialty Statistics -->
        <div class="card min-w-0 space-y-4 p-4 sm:p-6">
          <h2 class="text-base font-bold text-gray-900">Specialty Department Performance</h2>
          <div class="overflow-x-auto">
            <table class="min-w-[480px] w-full text-left text-sm text-gray-700">
              <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
                <tr>
                  <th class="px-3 py-2">Specialty</th>
                  <th class="px-3 py-2 text-center">Doctors</th>
                  <th class="px-3 py-2 text-center">Services</th>
                  <th class="px-3 py-2 text-center">Appts</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="spec in reportsStore.overview.specialty_stats" :key="spec.specialty_id" class="hover:bg-gray-50">
                  <td class="px-3 py-2 font-semibold text-gray-900">{{ spec.specialty_name }}</td>
                  <td class="px-3 py-2 text-center">{{ spec.doctor_count }}</td>
                  <td class="px-3 py-2 text-center">{{ spec.service_count }}</td>
                  <td class="px-3 py-2 text-center font-bold text-primary-700">{{ spec.appointment_count }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB 4: PEAK TIMES & DEMOGRAPHICS -->
      <div v-if="activeTab === 'peaks_demo'" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Peak Times -->
        <div class="card min-w-0 space-y-4 p-4 sm:p-6">
          <h2 class="text-base font-bold text-gray-900">Peak Booking Days & Hours</h2>

          <div class="space-y-4">
            <div>
              <h3 class="text-xs font-bold text-gray-600 uppercase mb-2">Busiest Days of Week</h3>
              <div class="space-y-2">
                <div v-for="d in reportsStore.overview.peak_times.busiest_days" :key="d.label" class="flex items-center gap-3">
                  <span class="w-24 text-xs font-semibold text-gray-700">{{ d.label }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
                    <div class="bg-blue-600 h-2.5 rounded-full" :style="{ width: `${Math.min((d.count / (reportsStore.overview.status_breakdown.total_count || 1)) * 100 * 3, 100)}%` }"></div>
                  </div>
                  <span class="text-xs font-mono font-bold text-gray-900 w-8 text-right">{{ d.count }}</span>
                </div>
              </div>
            </div>

            <div class="pt-4 border-t border-gray-100">
              <h3 class="text-xs font-bold text-gray-600 uppercase mb-2">Busiest Hours of Day</h3>
              <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <div v-for="h in reportsStore.overview.peak_times.busiest_hours" :key="h.label" class="bg-gray-50 p-2 rounded-lg border border-gray-100 flex justify-between items-center text-xs">
                  <span class="font-mono text-gray-600">{{ h.label }}</span>
                  <span class="font-bold text-primary-700">{{ h.count }} appts</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Demographics -->
        <div class="card min-w-0 space-y-4 p-4 sm:p-6">
          <h2 class="text-base font-bold text-gray-900">Patient Demographic Distribution</h2>

          <div class="space-y-6">
            <div>
              <h3 class="text-xs font-bold text-gray-600 uppercase mb-2">Gender Breakdown</h3>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div v-for="g in reportsStore.overview.demographics.gender_distribution" :key="g.label" class="bg-teal-50/50 p-3 rounded-lg border border-teal-100 text-center">
                  <div class="text-xs text-teal-700 font-medium">{{ g.label }}</div>
                  <div class="text-xl font-bold text-gray-900 mt-1">{{ g.count }}</div>
                </div>
              </div>
            </div>

            <div class="pt-4 border-t border-gray-100">
              <h3 class="text-xs font-bold text-gray-600 uppercase mb-2">Age Group Distribution</h3>
              <div class="space-y-2">
                <div v-for="a in reportsStore.overview.demographics.age_distribution" :key="a.label" class="flex items-center gap-3">
                  <span class="w-24 text-xs font-semibold text-gray-700">{{ a.label }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
                    <div class="bg-teal-600 h-2.5 rounded-full" :style="{ width: `${reportsStore.overview.demographics.total_patients ? (a.count / reportsStore.overview.demographics.total_patients * 100) : 0}%` }"></div>
                  </div>
                  <span class="text-xs font-mono font-bold text-gray-900 w-8 text-right">{{ a.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
