<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useDashboardStore } from '~/stores/dashboard'
import { useUsersService } from '~/services/users'
import type { User } from '~~/shared/types/User'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const usersService = useUsersService()

const activeTab = ref<'overview' | 'users'>('overview')
const usersList = ref<User[]>([])
const selectedRoleFilter = ref<string>('')
const loadingUsers = ref(false)

const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)

const appointmentChart = computed(() => {
  const summary = dashboardStore.adminSummary
  const items = [
    { label: 'Pending', value: summary?.pending_count || 0, color: '#f59e0b' },
    { label: 'Confirmed', value: summary?.confirmed_count || 0, color: '#10b981' },
    { label: 'Completed', value: summary?.completed_count || 0, color: '#3b82f6' },
    { label: 'Cancelled', value: summary?.cancelled_count || 0, color: '#ef4444' },
  ]
  const total = items.reduce((sum, item) => sum + item.value, 0)
  let current = 0
  const stops = items.map((item) => {
    const start = current
    current += total ? (item.value / total) * 100 : 0
    return `${item.color} ${start}% ${current}%`
  })
  return {
    items,
    total,
    background: total ? `conic-gradient(${stops.join(', ')})` : '#e5e7eb',
  }
})

const userRoleChart = computed(() => {
  const summary = dashboardStore.adminSummary
  const patients = summary?.total_patients || 0
  const doctors = summary?.total_doctors || 0
  const staff = summary?.total_staff || 0
  const admin = Math.max(0, (summary?.total_users || 0) - patients - doctors - staff)
  const items = [
    { label: 'Patients', value: patients, color: 'bg-primary-500' },
    { label: 'Doctors', value: doctors, color: 'bg-teal-500' },
    { label: 'Staff', value: staff, color: 'bg-blue-500' },
    { label: 'Admins', value: admin, color: 'bg-purple-500' },
  ]
  const maximum = Math.max(1, ...items.map((item) => item.value))
  return items.map((item) => ({
    ...item,
    percentage: (item.value / maximum) * 100,
  }))
})

onMounted(async () => {
  await Promise.all([
    dashboardStore.fetchAdminDashboard(),
    fetchUsers(),
  ])
})

const fetchUsers = async () => {
  loadingUsers.value = true
  try {
    usersList.value = await usersService.getUsers(selectedRoleFilter.value || undefined)
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to fetch users'
  } finally {
    loadingUsers.value = false
  }
}

watch(selectedRoleFilter, async () => {
  await fetchUsers()
})

const handleToggleUserActive = async (userId: string) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await usersService.toggleUserActive(userId)
    actionSuccess.value = 'User account active status toggled.'
    await fetchUsers()
    await dashboardStore.fetchAdminDashboard()
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update user status.'
  }
}
</script>

<template>
  <div class="page-container space-y-8">
    <section class="dashboard-banner flex flex-col items-start justify-between gap-5 md:flex-row md:items-center">
      <div class="min-w-0">
        <span class="dashboard-kicker">System administration</span>
        <h1 class="dashboard-display-title text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">Administration Dashboard</h1>
        <p class="mt-1 max-w-2xl text-sm text-slate-600">Monitor clinic operations, account activity, appointment volume, and configuration from one workspace.</p>
      </div>
      <NuxtLink to="/admin" class="dashboard-action-primary w-full shrink-0 justify-center py-2.5 text-sm md:w-auto">
        <LucideSettings class="h-4 w-4" />
        <span>Manage Clinic</span>
      </NuxtLink>
    </section>

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

    <!-- Navigation Tabs -->
    <div class="inline-flex w-full gap-1 rounded-2xl border border-slate-200 bg-slate-100/80 p-1 sm:w-auto">
      <button
        class="flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all sm:flex-none"
        :class="activeTab === 'overview' ? 'bg-white text-primary-700 shadow-sm ring-1 ring-slate-200' : 'text-slate-600 hover:text-slate-950'"
        @click="activeTab = 'overview'"
      >
        <LucideBarChart3 class="h-4 w-4" />
        <span>System Metrics Overview</span>
      </button>

      <button
        class="flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all sm:flex-none"
        :class="activeTab === 'users' ? 'bg-white text-primary-700 shadow-sm ring-1 ring-slate-200' : 'text-slate-600 hover:text-slate-950'"
        @click="activeTab = 'users'"
      >
        <LucideUsers class="h-4 w-4" />
        <span>User Accounts ({{ usersList.length }})</span>
      </button>
    </div>

    <!-- TAB 1: SYSTEM OVERVIEW -->
    <div v-if="activeTab === 'overview'" class="space-y-8">
      <!-- Loading State -->
      <div v-if="dashboardStore.loading" class="flex justify-center py-16">
        <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
      </div>

      <div v-else class="space-y-8">
        <!-- User Counts Grid -->
        <div class="space-y-3">
          <div><h2 class="text-base font-bold text-slate-950">Accounts overview</h2><p class="mt-1 text-sm text-slate-500">Current registered users by operational role.</p></div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="card relative overflow-hidden p-5">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">Total users</div>
              <div class="mt-2 text-3xl font-bold tracking-tight text-slate-950">{{ dashboardStore.adminSummary?.total_users || 0 }}</div>
            </div>

            <div class="card relative overflow-hidden p-5">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">Patients</div>
              <div class="mt-2 text-3xl font-bold tracking-tight text-slate-950">{{ dashboardStore.adminSummary?.total_patients || 0 }}</div>
            </div>

            <div class="card relative overflow-hidden p-5">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">Doctors</div>
              <div class="mt-2 text-3xl font-bold tracking-tight text-slate-950">{{ dashboardStore.adminSummary?.total_doctors || 0 }}</div>
              <p class="mt-1 text-xs text-slate-500">{{ dashboardStore.adminSummary?.active_doctors_count || 0 }} active</p>
            </div>

            <div class="card relative overflow-hidden p-5">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">Staff</div>
              <div class="mt-2 text-3xl font-bold tracking-tight text-slate-950">{{ dashboardStore.adminSummary?.total_staff || 0 }}</div>
            </div>
          </div>
        </div>

        <!-- Appointment Status Metrics -->
        <div class="space-y-3">
          <div><h2 class="text-base font-bold text-slate-950">Appointment metrics</h2><p class="mt-1 text-sm text-slate-500">Operational totals across the current appointment workflow.</p></div>
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div class="card relative overflow-hidden p-4 text-center">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-medium text-slate-500">Today's Total</div>
              <div class="mt-2 text-2xl font-bold text-slate-950">{{ dashboardStore.adminSummary?.today_appointments_count || 0 }}</div>
            </div>

            <div class="card relative overflow-hidden p-4 text-center">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-medium text-slate-500">Pending</div>
              <div class="mt-2 text-2xl font-bold text-slate-950">{{ dashboardStore.adminSummary?.pending_count || 0 }}</div>
            </div>

            <div class="card relative overflow-hidden p-4 text-center">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-medium text-slate-500">Confirmed</div>
              <div class="mt-2 text-2xl font-bold text-slate-950">{{ dashboardStore.adminSummary?.confirmed_count || 0 }}</div>
            </div>

            <div class="card relative overflow-hidden p-4 text-center">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-medium text-slate-500">Completed</div>
              <div class="mt-2 text-2xl font-bold text-slate-950">{{ dashboardStore.adminSummary?.completed_count || 0 }}</div>
            </div>

            <div class="card relative col-span-2 overflow-hidden p-4 text-center sm:col-span-1">
              <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
              <div class="text-xs font-medium text-slate-500">Cancelled</div>
              <div class="mt-2 text-2xl font-bold text-slate-950">{{ dashboardStore.adminSummary?.cancelled_count || 0 }}</div>
            </div>
          </div>
        </div>

        <!-- Dashboard Charts -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <section class="card p-6" aria-labelledby="appointment-chart-title">
            <div class="mb-6">
              <h2 id="appointment-chart-title" class="text-base font-bold text-gray-900">Appointment Status Distribution</h2>
              <p class="mt-1 text-xs text-gray-500">Current appointment totals grouped by status</p>
            </div>

            <div class="flex flex-col items-center gap-7 sm:flex-row sm:justify-center">
              <div
                class="relative h-44 w-44 shrink-0 rounded-full"
                :style="{ background: appointmentChart.background }"
                role="img"
                :aria-label="`${appointmentChart.total} appointments shown by status`"
              >
                <div class="absolute inset-8 flex flex-col items-center justify-center rounded-full bg-white shadow-inner">
                  <span class="text-3xl font-bold text-gray-900">{{ appointmentChart.total }}</span>
                  <span class="text-xs text-gray-500">Appointments</span>
                </div>
              </div>

              <div class="grid w-full grid-cols-2 gap-3 sm:w-auto sm:grid-cols-1">
                <div v-for="item in appointmentChart.items" :key="item.label" class="flex items-center gap-3">
                  <span class="h-3 w-3 shrink-0 rounded-full" :style="{ backgroundColor: item.color }"></span>
                  <span class="min-w-20 text-sm text-gray-600">{{ item.label }}</span>
                  <span class="ml-auto text-sm font-bold text-gray-900">{{ item.value }}</span>
                </div>
              </div>
            </div>
          </section>

          <section class="card p-6" aria-labelledby="user-chart-title">
            <div class="mb-6">
              <h2 id="user-chart-title" class="text-base font-bold text-gray-900">Users by Role</h2>
              <p class="mt-1 text-xs text-gray-500">Relative account totals across the four system roles</p>
            </div>

            <div class="space-y-5">
              <div v-for="item in userRoleChart" :key="item.label">
                <div class="mb-1.5 flex items-center justify-between text-sm">
                  <span class="font-medium text-gray-700">{{ item.label }}</span>
                  <span class="font-bold text-gray-900">{{ item.value }}</span>
                </div>
                <div class="h-4 overflow-hidden rounded-full bg-gray-100">
                  <div
                    class="h-full min-w-0 rounded-full transition-all duration-500"
                    :class="item.color"
                    :style="{ width: `${item.percentage}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Domain Catalog Metrics & Shortcuts -->
        <div class="space-y-4">
          <h2 class="text-base font-bold text-gray-900">Clinic Infrastructure & Management Shortcuts</h2>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <NuxtLink
              to="/admin"
              class="card card-hover flex items-center justify-between group p-5"
            >
              <div>
                <div class="text-xs text-gray-500 font-medium">Specialties Catalog</div>
                <div class="text-2xl font-bold text-gray-900 mt-1">{{ dashboardStore.adminSummary?.total_specialties || 0 }} Specialties</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-primary-700 ring-1 ring-primary-100 transition-colors group-hover:bg-primary-600 group-hover:text-white">
                <LucideAward class="h-5 w-5" />
              </div>
            </NuxtLink>

            <NuxtLink
              to="/admin"
              class="card card-hover flex items-center justify-between group p-5"
            >
              <div>
                <div class="text-xs text-gray-500 font-medium">Clinic Services Catalog</div>
                <div class="text-2xl font-bold text-gray-900 mt-1">{{ dashboardStore.adminSummary?.total_services || 0 }} Services</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-primary-700 ring-1 ring-primary-100 transition-colors group-hover:bg-primary-600 group-hover:text-white">
                <LucideHeartHandshake class="h-5 w-5" />
              </div>
            </NuxtLink>

            <NuxtLink
              to="/admin/schedules"
              class="card card-hover flex items-center justify-between group p-5"
            >
              <div>
                <div class="text-xs text-gray-500 font-medium">Doctor Working Hours</div>
                <div class="text-sm font-bold text-gray-900 mt-2">Manage Schedules &rarr;</div>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-primary-700 ring-1 ring-primary-100 transition-colors group-hover:bg-primary-600 group-hover:text-white">
                <LucideClock class="h-5 w-5" />
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: USER ACCOUNTS MANAGEMENT -->
    <div v-if="activeTab === 'users'" class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-lg font-bold text-gray-900">User Account Directory</h2>
          <p class="text-xs text-gray-500">Filter accounts by role and manage active status</p>
        </div>

        <div class="flex gap-3 w-full sm:w-auto">
          <select v-model="selectedRoleFilter" class="px-3 py-2 border border-gray-300 rounded-lg text-xs text-gray-900 bg-white">
            <option value="">All Roles</option>
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
            <option value="staff">Staff</option>
            <option value="admin">Admin</option>
          </select>

        </div>
      </div>

      <div v-if="loadingUsers" class="flex justify-center py-12">
        <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
      </div>

      <div v-else class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold text-xs uppercase">
            <tr>
              <th class="px-4 py-3">User</th>
              <th class="px-4 py-3">Role</th>
              <th class="px-4 py-3">Email Status</th>
              <th class="px-4 py-3">Account Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="u in usersList" :key="u.id" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="font-bold text-gray-900">{{ u.name }}</div>
                <div class="text-xs text-gray-500 font-mono">{{ u.email }}</div>
              </td>
              <td class="px-4 py-3">
                <span
                  class="px-2.5 py-0.5 rounded text-xs font-semibold capitalize"
                  :class="{
                    'bg-purple-100 text-purple-800': u.role === 'admin',
                    'bg-blue-100 text-blue-800': u.role === 'staff',
                    'bg-teal-100 text-teal-800': u.role === 'doctor',
                    'bg-gray-100 text-gray-800': u.role === 'patient',
                  }"
                >
                  {{ u.role }}
                </span>
              </td>
              <td class="px-4 py-3">
                <BaseStatusBadge :status="u.is_email_verified ? 'Verified' : 'Unverified'" />
              </td>
              <td class="px-4 py-3">
                <BaseStatusBadge :status="u.is_active ? 'Active' : 'Deactivated'" />
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  v-if="u.id !== authStore.user?.id"
                  class="text-xs font-medium transition-colors"
                  :class="u.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'"
                  @click="handleToggleUserActive(u.id)"
                >
                  {{ u.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>
