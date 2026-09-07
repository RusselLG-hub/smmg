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
  await dashboardStore.fetchDoctorDashboard()
})

const handleUpdateStatus = async (id: string, newStatus: string) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await appointmentsStore.updateStatus(id, newStatus)
    actionSuccess.value = `Consultation marked as ${newStatus}.`
    await dashboardStore.fetchDoctorDashboard()
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update appointment status.'
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
  <div class="page-container space-y-8">
    <!-- Welcome Header Banner -->
    <div class="dashboard-banner flex flex-col items-start justify-between gap-5 sm:flex-row sm:items-center">
      <div>
        <span class="dashboard-kicker">
          Doctor Portal
        </span>
        <h1 class="text-3xl font-bold tracking-tight">Welcome, Dr. {{ authStore.user?.name }}</h1>
        <p class="mt-1 text-sm text-slate-600">Manage today's consultations and weekly working schedules</p>
      </div>

      <div class="flex flex-wrap gap-3">
        <NuxtLink
          to="/doctor/profile"
          class="dashboard-action-muted text-sm"
        >
          <LucideUser class="h-4 w-4" />
          <span>My Profile & Avatar</span>
        </NuxtLink>

        <NuxtLink
          to="/admin/schedules"
          class="dashboard-action-muted text-sm"
        >
          <LucideClock class="h-4 w-4" />
          <span>My Working Hours</span>
        </NuxtLink>

        <NuxtLink
          to="/doctor/appointments"
          class="dashboard-action-primary text-sm"
        >
          <LucideClipboardList class="h-4 w-4" />
          <span>All Consultations</span>
        </NuxtLink>
      </div>
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
      <!-- Stat Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <BaseStatCard
          label="Today's Consultations"
          :value="dashboardStore.doctorSummary?.today_count || 0"
          variant="success"
        >
          <template #icon>
            <LucideStethoscope class="h-6 w-6 text-teal-600" />
          </template>
        </BaseStatCard>

        <BaseStatCard
          label="Upcoming Appointments"
          :value="dashboardStore.doctorSummary?.upcoming_count || 0"
          variant="info"
        >
          <template #icon>
            <LucideCalendarCheck class="h-6 w-6 text-blue-600" />
          </template>
        </BaseStatCard>

        <BaseStatCard
          label="Active Schedules"
          :value="dashboardStore.doctorSummary?.schedule_count || 0"
          variant="default"
        >
          <template #icon>
            <LucideClock class="h-6 w-6 text-purple-600" />
          </template>
        </BaseStatCard>
      </div>

      <!-- Today's Consultations List -->
      <div class="card p-6 space-y-4">
        <div class="flex items-center justify-between pb-4 border-b border-gray-100">
          <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
            <LucideCalendar class="h-5 w-5 text-teal-600" />
            <span>Today's Consultation Schedule</span>
          </h2>
          <NuxtLink to="/doctor/appointments" class="text-xs font-semibold text-teal-700 hover:underline">
            Full Consultation History &rarr;
          </NuxtLink>
        </div>

        <div v-if="!dashboardStore.doctorSummary?.today_appointments || dashboardStore.doctorSummary.today_appointments.length === 0" class="py-8 text-center bg-gray-50 rounded-xl border border-gray-200">
          <LucideCalendarX class="h-10 w-10 text-gray-400 mx-auto mb-2" />
          <h4 class="text-base font-semibold text-gray-900">No Consultations Today</h4>
          <p class="text-xs text-gray-500 mt-1">You have no appointments scheduled for today's date.</p>
          <NuxtLink
            to="/doctor/appointments"
            class="btn-primary inline-flex items-center gap-1.5 mt-3 text-xs"
          >
            <LucideClipboardList class="h-4 w-4" />
            <span>View All Consultations ({{ dashboardStore.doctorSummary?.upcoming_count || 0 }} upcoming) &rarr;</span>
          </NuxtLink>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm text-gray-700">
            <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
              <tr>
                <th class="px-4 py-3">Time</th>
                <th class="px-4 py-3">Patient</th>
                <th class="px-4 py-3">Service / Reason</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="appt in dashboardStore.doctorSummary.today_appointments" :key="appt.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-mono font-bold text-gray-900 whitespace-nowrap">
                  {{ formatTime(appt.scheduled_at) }}
                </td>
                <td class="px-4 py-3">
                  <div class="font-semibold text-gray-900">{{ appt.patient.user.name }}</div>
                  <div class="text-xs text-gray-500 font-mono">{{ appt.appointment_reference }}</div>
                </td>
                <td class="px-4 py-3">
                  <span v-if="appt.service" class="font-medium text-gray-800">{{ appt.service.name }}</span>
                  <span v-else class="text-gray-400 italic">General Consultation</span>
                </td>
                <td class="px-4 py-3">
                  <BaseStatusBadge :status="appt.status" />
                </td>
                <td class="px-4 py-3 text-right whitespace-nowrap">
                  <button
                    v-if="appt.status === 'confirmed'"
                    class="px-3 py-1 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700 shadow-sm"
                    @click="handleUpdateStatus(appt.id, 'completed')"
                  >
                    Mark Completed
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
