<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useReportsStore } from '~/stores/reports'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const reportsStore = useReportsStore()

const customStartDate = ref('')
const customEndDate = ref('')

onMounted(async () => {
  await reportsStore.fetchDoctorPersonal()
  if (reportsStore.doctorPersonal) {
    customStartDate.value = reportsStore.doctorPersonal.start_date
    customEndDate.value = reportsStore.doctorPersonal.end_date
  }
})

const handleApplyFilter = async () => {
  await reportsStore.fetchDoctorPersonal(customStartDate.value, customEndDate.value)
}

const maxVolumeCount = computed(() => {
  if (!reportsStore.doctorPersonal?.volume_trend || reportsStore.doctorPersonal.volume_trend.length === 0) return 1
  return Math.max(...reportsStore.doctorPersonal.volume_trend.map((v) => v.count), 1)
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    <!-- Header Banner -->
    <section class="dashboard-banner flex flex-col items-start justify-between gap-5 sm:flex-row sm:items-center">
      <div>
        <span class="dashboard-kicker">
          Doctor Analytics
        </span>
        <h1 class="dashboard-display-title text-3xl font-bold tracking-tight text-slate-950">Personal Consultation Statistics</h1>
        <p class="mt-1 text-sm text-slate-600">Dr. {{ authStore.user?.name }} — Track your consultation volume, completion rate, and service usage</p>
      </div>

      <NuxtLink
        to="/doctor/dashboard"
        class="dashboard-action-muted"
      >
        <LucideLayoutDashboard class="h-4 w-4 text-blue-700" />
        <span>Return to Dashboard</span>
      </NuxtLink>
    </section>

    <!-- Date Filter Controls -->
    <div class="card p-5">
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

    <div v-else-if="reportsStore.doctorPersonal" class="space-y-8">
      <!-- Personal Metric Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-6">
        <div class="card p-6">
          <div class="text-xs font-medium text-gray-500">Total Consultations</div>
          <div class="text-3xl font-bold text-gray-900 mt-1">{{ reportsStore.doctorPersonal.status_breakdown.total_count }}</div>
        </div>

        <div class="card p-6">
          <div class="text-xs font-medium text-gray-500">Completed</div>
          <div class="text-3xl font-bold text-green-700 mt-1">{{ reportsStore.doctorPersonal.status_breakdown.completed_count }}</div>
        </div>

        <div class="card p-6">
          <div class="text-xs font-medium text-gray-500">Completion Rate</div>
          <div class="text-3xl font-bold text-teal-700 mt-1">{{ reportsStore.doctorPersonal.status_breakdown.completion_rate_pct }}%</div>
        </div>

        <div class="card p-6">
          <div class="text-xs font-medium text-gray-500">Cancelled</div>
          <div class="text-3xl font-bold text-red-700 mt-1">{{ reportsStore.doctorPersonal.status_breakdown.cancelled_count }}</div>
        </div>
      </div>

      <!-- Volume & Service Usage -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Volume Trend -->
        <div class="card p-6 space-y-4">
          <h2 class="text-base font-bold text-gray-900">Consultation Volume Trend</h2>

          <div v-if="reportsStore.doctorPersonal.volume_trend.length === 0" class="py-12 text-center text-xs text-gray-500">
            No consultations recorded in this date range.
          </div>

          <div v-else class="h-48 flex items-end gap-2 pt-6 overflow-x-auto">
            <div
              v-for="v in reportsStore.doctorPersonal.volume_trend"
              :key="v.date"
              class="flex-1 min-w-[28px] flex flex-col items-center gap-2 h-full justify-end group"
            >
              <div class="text-[10px] font-bold text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                {{ v.count }}
              </div>
              <div
                class="w-full bg-teal-600 hover:bg-teal-700 rounded-t-md transition-all"
                :style="{ height: `${(v.count / maxVolumeCount) * 80}%` }"
              ></div>
              <div class="text-[9px] font-mono text-gray-400 rotate-45 origin-left whitespace-nowrap mt-1">
                {{ v.date.substring(5) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Service Breakdown -->
        <div class="card p-6 space-y-4">
          <h2 class="text-base font-bold text-gray-900">Your Consultation Services</h2>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-gray-700">
              <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
                <tr>
                  <th class="px-3 py-2">Service</th>
                  <th class="px-3 py-2 text-center">Consultations</th>
                  <th class="px-3 py-2 text-center">% Share</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="srv in reportsStore.doctorPersonal.service_stats" :key="srv.service_name" class="hover:bg-gray-50">
                  <td class="px-3 py-2 font-semibold text-gray-900">{{ srv.service_name }}</td>
                  <td class="px-3 py-2 text-center font-bold">{{ srv.appointment_count }}</td>
                  <td class="px-3 py-2 text-center font-medium text-teal-700">{{ srv.percentage_of_total }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
