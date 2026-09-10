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

const todayStr = new Date().toISOString().split('T')[0]
const activeTab = ref<'all' | 'today'>('all')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([
    dashboardStore.fetchStaffDashboard(),
    appointmentsStore.fetchAdminAppointments(),
  ])
})

const handleUpdateStatus = async (id: string, newStatus: string) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await appointmentsStore.updateStatus(id, newStatus)
    actionSuccess.value = `Status updated to ${newStatus}.`
    await Promise.all([
      dashboardStore.fetchStaffDashboard(),
      appointmentsStore.fetchAdminAppointments(),
    ])
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update status.'
  }
}

const formatDate = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
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
    <!-- Header Banner -->
    <div class="dashboard-banner flex flex-col items-start justify-between gap-5 sm:flex-row sm:items-center">
      <div>
        <span class="dashboard-kicker">
          Staff Operations Desk
        </span>
        <h1 class="text-3xl font-bold tracking-tight">Daily Operations Dashboard</h1>
        <p class="mt-1 text-sm text-slate-600">Manage today's clinic appointments and doctor availability</p>
      </div>

      <div class="flex flex-wrap gap-3">
        <NuxtLink
          to="/admin/schedules"
          class="dashboard-action-muted py-2.5 text-sm"
        >
          <LucideClock class="h-4 w-4" />
          <span>Doctor Schedule</span>
        </NuxtLink>

        <NuxtLink
          to="/admin/appointments"
          class="dashboard-action-primary py-2.5 text-sm"
        >
          <LucideCalendarCheck class="h-4 w-4" />
          <span>Master Appointments</span>
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

      <!-- Clinic Master Bookings & Consultations List -->
      <div class="card p-6 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-gray-100">
          <div class="flex flex-wrap items-center gap-3">
            <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              <LucideClipboardCheck class="h-5 w-5 text-blue-600" />
              <span>Clinic Bookings & Consultations</span>
            </h2>
            <div class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-0.5 text-xs font-medium">
              <button
                type="button"
                class="px-2.5 py-1 rounded-md transition-colors"
                :class="activeTab === 'all' ? 'bg-white font-semibold text-primary-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                @click="activeTab = 'all'"
              >
                All Bookings ({{ appointmentsStore.adminAppointments.length }})
              </button>
              <button
                type="button"
                class="px-2.5 py-1 rounded-md transition-colors"
                :class="activeTab === 'today' ? 'bg-white font-semibold text-primary-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                @click="activeTab = 'today'"
              >
                Today Only ({{ dashboardStore.staffSummary?.today_count || 0 }})
              </button>
            </div>
          </div>

          <NuxtLink to="/admin/appointments" class="text-xs font-semibold text-blue-600 hover:underline flex items-center gap-1">
            <span>Directory & Filters &rarr;</span>
          </NuxtLink>
        </div>

        <!-- All Bookings View -->
        <div v-if="activeTab === 'all'">
          <div v-if="appointmentsStore.adminAppointments.length === 0" class="py-8 text-center bg-gray-50 rounded-xl border border-gray-200">
            <LucideCalendarX class="h-10 w-10 text-gray-400 mx-auto mb-2" />
            <h4 class="text-base font-semibold text-gray-900">No Clinic Bookings</h4>
            <p class="text-xs text-gray-500 mt-1">There are currently no patient appointments booked in the system.</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-sm text-gray-700">
              <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
                <tr>
                  <th class="px-4 py-3">Scheduled Time</th>
                  <th class="px-4 py-3">Reference / Patient</th>
                  <th class="px-4 py-3">Assigned Doctor</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3 text-right">Quick Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="appt in appointmentsStore.adminAppointments" :key="appt.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">
                    <div class="flex items-center gap-1.5">
                      <span>{{ formatDate(appt.scheduled_at) }}</span>
                      <span
                        v-if="appt.scheduled_at.startsWith(todayStr)"
                        class="px-1.5 py-0.5 text-[10px] font-bold rounded bg-green-100 text-green-700"
                      >
                        Today
                      </span>
                    </div>
                    <div class="font-mono text-xs text-gray-500">{{ formatTime(appt.scheduled_at) }}</div>
                  </td>
                  <td class="px-4 py-3">
                    <div class="font-mono text-xs text-gray-500 mb-0.5">{{ appt.appointment_reference }}</div>
                    <div class="font-semibold text-gray-900">{{ appt.patient.user.name }}</div>
                    <div class="text-xs text-gray-500">{{ appt.patient.user.email }}</div>
                  </td>
                  <td class="px-4 py-3 font-medium text-gray-900">
                    <div>Dr. {{ appt.doctor.user.name }}</div>
                    <div v-if="appt.doctor.specialty" class="text-xs text-teal-600 font-normal">{{ appt.doctor.specialty.name }}</div>
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
                      v-if="appt.status === 'pending' || appt.status === 'confirmed'"
                      class="px-2.5 py-1 border border-red-200 text-red-600 rounded text-xs font-medium hover:bg-red-50"
                      @click="handleUpdateStatus(appt.id, 'cancelled')"
                    >
                      Cancel
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Today Only View -->
        <div v-else>
          <div v-if="!dashboardStore.staffSummary?.today_appointments || dashboardStore.staffSummary.today_appointments.length === 0" class="py-8 text-center bg-gray-50 rounded-xl border border-gray-200">
            <LucideCalendarX class="h-10 w-10 text-gray-400 mx-auto mb-2" />
            <h4 class="text-base font-semibold text-gray-900">No Appointments Today</h4>
            <p class="text-xs text-gray-500 mt-1">There are no appointments scheduled for today's date.</p>
            <button
              type="button"
              class="btn-primary mt-3 text-xs"
              @click="activeTab = 'all'"
            >
              View All Bookings ({{ appointmentsStore.adminAppointments.length }})
            </button>
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
                      v-if="appt.status === 'pending' || appt.status === 'confirmed'"
                      class="px-2.5 py-1 border border-red-200 text-red-600 rounded text-xs font-medium hover:bg-red-50"
                      @click="handleUpdateStatus(appt.id, 'cancelled')"
                    >
                      Cancel
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
