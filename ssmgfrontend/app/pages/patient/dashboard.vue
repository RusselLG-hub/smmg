<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useDashboardStore } from '~/stores/dashboard'

definePageMeta({
  middleware: 'auth',
})

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()

onMounted(async () => {
  await dashboardStore.fetchPatientDashboard()
})

const formatDate = (isoStr: string) => {
  const d = new Date(isoStr)
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
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
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    <!-- Welcome Header Banner -->
    <div class="bg-gradient-to-r from-primary-600 to-teal-600 rounded-2xl p-8 text-white shadow-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <span class="inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-semibold uppercase tracking-wider mb-2 backdrop-blur-sm">
          Patient Portal
        </span>
        <h1 class="text-3xl font-bold tracking-tight">Welcome back, {{ authStore.user?.name }}!</h1>
        <p class="text-primary-100 text-sm mt-1">Manage your appointment bookings and healthcare consultations</p>
      </div>

      <div class="flex gap-3">
        <NuxtLink
          to="/ai-assistant"
          class="inline-flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white font-medium text-xs rounded-xl transition-colors backdrop-blur-sm"
        >
          <LucideBot class="h-4 w-4" />
          <span>AI Assistant</span>
        </NuxtLink>

        <NuxtLink
          to="/doctors"
          class="inline-flex items-center gap-2 px-5 py-2 bg-white text-primary-700 font-semibold text-xs rounded-xl hover:bg-primary-50 transition-colors shadow"
        >
          <LucideCalendarPlus class="h-4 w-4 text-primary-600" />
          <span>Book Consultation</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="dashboardStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <div v-else class="space-y-8">
      <!-- Summary Metrics Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <BaseStatCard
          label="Upcoming Appointments"
          :value="dashboardStore.patientSummary?.upcoming_count || 0"
          variant="info"
        >
          <template #icon>
            <LucideCalendarCheck class="h-6 w-6" />
          </template>
        </BaseStatCard>

        <BaseStatCard
          label="Completed Consultations"
          :value="dashboardStore.patientSummary?.completed_count || 0"
          variant="success"
        >
          <template #icon>
            <LucideCheckCircle2 class="h-6 w-6" />
          </template>
        </BaseStatCard>

        <div class="card flex items-center justify-between sm:col-span-2 lg:col-span-1">
          <div>
            <div class="text-xs font-medium text-gray-500">Account Status</div>
            <div class="text-sm font-bold text-green-700 mt-1 flex items-center gap-1.5">
              <span class="h-2 w-2 rounded-full bg-green-500"></span>
              Active Patient Account
            </div>
          </div>
          <div class="h-12 w-12 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
            <LucideUserCheck class="h-6 w-6" />
          </div>
        </div>
      </div>

      <!-- Next Upcoming Appointment Card -->
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4">
        <div class="flex items-center justify-between pb-4 border-b border-gray-100">
          <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
            <LucideClock class="h-5 w-5 text-primary-600" />
            <span>Next Scheduled Appointment</span>
          </h2>
          <NuxtLink to="/patient/appointments" class="text-xs font-semibold text-primary-600 hover:underline">
            View All &rarr;
          </NuxtLink>
        </div>

        <div v-if="!dashboardStore.patientSummary?.upcoming_appointment" class="py-8 text-center bg-gray-50 rounded-xl border border-gray-200">
          <LucideCalendarOff class="h-10 w-10 text-gray-400 mx-auto mb-2" />
          <h4 class="text-base font-semibold text-gray-900">No Upcoming Appointments</h4>
          <p class="text-xs text-gray-500 mt-1">You have no upcoming consultations scheduled.</p>
          <NuxtLink
            to="/doctors"
            class="inline-flex items-center gap-1.5 px-4 py-2 mt-4 bg-primary-600 text-white rounded-lg text-xs font-semibold hover:bg-primary-700"
          >
            <LucidePlus class="h-3.5 w-3.5" />
            <span>Schedule Appointment</span>
          </NuxtLink>
        </div>

        <div v-else class="p-6 bg-primary-50/40 rounded-xl border border-primary-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-mono text-xs font-bold text-gray-700 bg-white px-2 py-0.5 rounded border border-gray-200">
                {{ dashboardStore.patientSummary.upcoming_appointment.appointment_reference }}
              </span>
              <BaseStatusBadge :status="dashboardStore.patientSummary.upcoming_appointment.status" />
            </div>

            <div class="text-xl font-bold text-gray-900 pt-1">
              Dr. {{ dashboardStore.patientSummary.upcoming_appointment.doctor.user.name }}
            </div>

            <div v-if="dashboardStore.patientSummary.upcoming_appointment.doctor.specialty" class="text-xs font-medium text-teal-700">
              {{ dashboardStore.patientSummary.upcoming_appointment.doctor.specialty.name }}
            </div>
          </div>

          <div class="space-y-2 text-right w-full sm:w-auto">
            <div class="bg-white p-3 rounded-lg border border-primary-200 text-xs space-y-1 text-gray-800 font-medium">
              <div class="flex items-center gap-2 justify-end">
                <LucideCalendar class="h-3.5 w-3.5 text-primary-600" />
                <span>{{ formatDate(dashboardStore.patientSummary.upcoming_appointment.scheduled_at) }}</span>
              </div>
              <div class="flex items-center gap-2 justify-end font-mono">
                <LucideClock class="h-3.5 w-3.5 text-primary-600" />
                <span>{{ formatTime(dashboardStore.patientSummary.upcoming_appointment.scheduled_at) }}</span>
              </div>
            </div>

            <NuxtLink
              to="/patient/appointments"
              class="inline-block text-xs font-semibold text-primary-700 hover:underline"
            >
              Manage Appointment &rarr;
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Quick Action Shortcuts -->
      <div class="space-y-4">
        <h2 class="text-lg font-bold text-gray-900">Quick Actions</h2>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <NuxtLink
            to="/ai-assistant"
            class="card card-hover group bg-teal-50/20 border-teal-200 hover:border-teal-400"
          >
            <div class="h-10 w-10 rounded-lg bg-teal-100 text-teal-700 flex items-center justify-center mb-3 group-hover:bg-teal-600 group-hover:text-white transition-colors">
              <LucideBot class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">AI Health Assistant</h3>
            <p class="text-xs text-gray-500 mt-1">First-aid guidance & general health questions</p>
          </NuxtLink>

          <NuxtLink
            to="/doctors"
            class="card card-hover group"
          >
            <div class="h-10 w-10 rounded-lg bg-primary-100 text-primary-600 flex items-center justify-center mb-3 group-hover:bg-primary-600 group-hover:text-white transition-colors">
              <LucideStethoscope class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">Browse Doctors</h3>
            <p class="text-xs text-gray-500 mt-1">Find healthcare specialists and check availability</p>
          </NuxtLink>

          <NuxtLink
            to="/services"
            class="card card-hover group"
          >
            <div class="h-10 w-10 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center mb-3 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <LucideHeartHandshake class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">Clinic Services</h3>
            <p class="text-xs text-gray-500 mt-1">Explore specialized medical services and consultations</p>
          </NuxtLink>

          <NuxtLink
            to="/patient/appointments"
            class="card card-hover group"
          >
            <div class="h-10 w-10 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center mb-3 group-hover:bg-purple-600 group-hover:text-white transition-colors">
              <LucideCalendarCheck class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">My Appointments</h3>
            <p class="text-xs text-gray-500 mt-1">View booking history, cancel, or reschedule</p>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
