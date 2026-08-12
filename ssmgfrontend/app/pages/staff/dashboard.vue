<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useDashboardStore } from '~/stores/dashboard'
import { useAppointmentsStore } from '~/stores/appointments'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const appointmentsStore = useAppointmentsStore()

const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

onMounted(async () => {
  await dashboardStore.fetchStaffDashboard()
})

const handleUpdateStatus = async (id: string, newStatus: string) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await appointmentsStore.updateStatus(id, newStatus)
    actionSuccess.value = `Status updated to ${newStatus}.`
    await dashboardStore.fetchStaffDashboard()
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update status.'
  }
}

const formatTime = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    <!-- Header Banner -->
    <div class="bg-gradient-to-r from-blue-700 to-indigo-700 rounded-2xl p-8 text-white shadow-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <span class="inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-semibold uppercase tracking-wider mb-2 backdrop-blur-sm">
          Staff Operations Desk
        </span>
        <h1 class="text-3xl font-bold tracking-tight">Daily Operations Dashboard</h1>
        <p class="text-blue-100 text-sm mt-1">Manage today's clinic appointments and doctor availability</p>
      </div>

      <NuxtLink
        to="/admin/appointments"
        class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-blue-700 font-semibold text-sm rounded-xl hover:bg-blue-50 transition-colors shadow"
      >
        <LucideCalendarCheck class="h-4 w-4 text-blue-600" />
        <span>Master Appointments</span>
      </NuxtLink>
    </div>

    <!-- Alert Notifications -->
    <div v-if="actionSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideCheckCircle2 class="h-5 w-5 text-green-500" />
        <span>{{ actionSuccess }}</span>
      </div>
      <button class="text-green-700 font-bold" @click="actionSuccess = null">&times;</button>
    </div>

    <div v-if="actionError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideAlertCircle class="h-5 w-5 text-red-500" />
        <span>{{ actionError }}</span>
      </div>
      <button class="text-red-700 font-bold" @click="actionError = null">&times;</button>
    </div>

    <!-- Loading State -->
    <div v-if="dashboardStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <div v-else class="space-y-8">
      <!-- Operational Metric Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div class="card p-4 text-center">
          <div class="text-xs font-medium text-gray-500">Today's Total</div>
          <div class="text-2xl font-bold text-gray-900 mt-1">{{ dashboardStore.staffSummary?.today_count || 0 }}</div>
        </div>

        <div class="card p-4 text-center bg-amber-50/30 border-amber-200">
          <div class="text-xs font-medium text-amber-700">Pending</div>
          <div class="text-2xl font-bold text-amber-800 mt-1">{{ dashboardStore.staffSummary?.pending_count || 0 }}</div>
        </div>

        <div class="card p-4 text-center bg-green-50/30 border-green-200">
          <div class="text-xs font-medium text-green-700">Confirmed</div>
          <div class="text-2xl font-bold text-green-800 mt-1">{{ dashboardStore.staffSummary?.confirmed_count || 0 }}</div>
        </div>

        <div class="card p-4 text-center bg-blue-50/30 border-blue-200">
          <div class="text-xs font-medium text-blue-700">Completed</div>
          <div class="text-2xl font-bold text-blue-800 mt-1">{{ dashboardStore.staffSummary?.completed_count || 0 }}</div>
        </div>

        <div class="card p-4 text-center bg-red-50/30 border-red-200 col-span-2 sm:col-span-1">
          <div class="text-xs font-medium text-red-700">Cancelled</div>
          <div class="text-2xl font-bold text-red-800 mt-1">{{ dashboardStore.staffSummary?.cancelled_count || 0 }}</div>
        </div>
      </div>

      <!-- Today's Master List -->
      <div class="card p-6 space-y-4">
        <div class="flex items-center justify-between pb-4 border-b border-gray-100">
          <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
            <LucideClipboardCheck class="h-5 w-5 text-blue-600" />
            <span>Today's Clinic Appointments</span>
          </h2>
          <NuxtLink to="/admin/appointments" class="text-xs font-semibold text-blue-600 hover:underline">
            All Appointments Portal &rarr;
          </NuxtLink>
        </div>

        <div v-if="!dashboardStore.staffSummary?.today_appointments || dashboardStore.staffSummary.today_appointments.length === 0" class="py-8 text-center bg-gray-50 rounded-xl border border-gray-200">
          <LucideCalendarX class="h-10 w-10 text-gray-400 mx-auto mb-2" />
          <h4 class="text-base font-semibold text-gray-900">No Appointments Today</h4>
          <p class="text-xs text-gray-500 mt-1">There are no appointments scheduled for today's date.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm text-gray-700">
            <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
              <tr>
                <th class="px-4 py-3">Time</th>
                <th class="px-4 py-3">Reference / Patient</th>
                <th class="px-4 py-3">Assigned Doctor</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3 text-right">Quick Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="appt in dashboardStore.staffSummary.today_appointments" :key="appt.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-mono font-bold text-gray-900 whitespace-nowrap">
                  {{ formatTime(appt.scheduled_at) }}
                </td>
                <td class="px-4 py-3">
                  <div class="font-mono text-xs text-gray-500 mb-0.5">{{ appt.appointment_reference }}</div>
                  <div class="font-semibold text-gray-900">{{ appt.patient.user.name }}</div>
                </td>
                <td class="px-4 py-3 font-medium text-gray-900">
                  Dr. {{ appt.doctor.user.name }}
                </td>
                <td class="px-4 py-3">
                  <BaseStatusBadge :status="appt.status" />
                </td>
                <td class="px-4 py-3 text-right whitespace-nowrap space-x-2">
                  <button
                    v-if="appt.status === 'pending'"
                    class="px-2.5 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700"
                    @click="handleUpdateStatus(appt.id, 'confirmed')"
                  >
                    Confirm
                  </button>
                  <button
                    v-if="appt.status === 'confirmed'"
                    class="px-2.5 py-1 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700"
                    @click="handleUpdateStatus(appt.id, 'completed')"
                  >
                    Mark Complete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
