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
    hour12: true,
  })
}
</script>

<template>
  <div class="page-container space-y-8">
    <!-- Welcome Header Banner -->
    <div class="dashboard-banner flex flex-col items-start justify-between gap-5 sm:flex-row sm:items-center">
      <div>
        <span class="dashboard-kicker">
          Patient Portal
        </span>
        <h1 class="text-3xl font-bold tracking-tight">Welcome back, {{ authStore.user?.name }}!</h1>
        <p class="mt-1 text-sm text-slate-600">Manage your appointment bookings and healthcare consultations</p>
      </div>

      <div class="flex gap-3">
        <NuxtLink
          to="/ai-assistant"
          class="dashboard-action-muted"
        >
          <LucideBot class="h-4 w-4" />
          <span>AI Assistant</span>
        </NuxtLink>

        <NuxtLink
          to="/book"
          class="dashboard-action-primary"
        >
          <LucideCalendarPlus class="h-4 w-4" />
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
      <div class="card p-6 sm:p-7 space-y-5">
        <!-- Card Header -->
        <div class="flex items-center justify-between pb-4 border-b border-gray-100">
          <div class="flex items-center gap-2.5">
            <span class="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <h2 class="text-base sm:text-lg font-bold text-gray-900 flex items-center gap-2">
              <LucideCalendarClock class="h-5 w-5 text-primary-600" />
              <span>Next Scheduled Appointment</span>
            </h2>
          </div>
          <NuxtLink
            to="/patient/appointments"
            class="inline-flex items-center gap-1 text-xs font-bold text-primary-700 hover:text-primary-800 hover:underline"
          >
            <span>View All</span>
            <LucideArrowRight class="h-3.5 w-3.5" />
          </NuxtLink>
        </div>

        <!-- Empty State -->
        <div v-if="!dashboardStore.patientSummary?.upcoming_appointment" class="py-10 text-center bg-slate-50/60 rounded-2xl border border-dashed border-slate-200">
          <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white border border-slate-200 text-slate-400 mb-3 shadow-2xs">
            <LucideCalendarOff class="h-6 w-6" />
          </div>
          <h4 class="text-sm font-bold text-gray-900">No Upcoming Appointments</h4>
          <p class="text-xs text-gray-500 mt-1 max-w-sm mx-auto">You do not have any pending or confirmed consultations on schedule.</p>
          <NuxtLink
            to="/book"
            class="btn-primary mt-4 inline-flex items-center gap-2 text-xs"
          >
            <LucideCalendarPlus class="h-4 w-4" />
            <span>Schedule Appointment</span>
          </NuxtLink>
        </div>

        <!-- Active Upcoming Appointment Card -->
        <div v-else class="space-y-4">
          <!-- Doctor & Schedule Highlights Box -->
          <div class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white via-slate-50/50 to-teal-50/30 p-5 sm:p-6 shadow-2xs flex flex-col md:flex-row justify-between md:items-center gap-5">
            <!-- Left: Doctor info -->
            <div class="flex items-start gap-4">
              <div class="h-14 w-14 rounded-2xl bg-teal-50 border border-teal-200/80 text-teal-700 flex items-center justify-center font-bold text-lg shrink-0 overflow-hidden shadow-2xs">
                <img
                  v-if="dashboardStore.patientSummary.upcoming_appointment.doctor.profile_image_url"
                  :src="dashboardStore.patientSummary.upcoming_appointment.doctor.profile_image_url"
                  :alt="dashboardStore.patientSummary.upcoming_appointment.doctor.user.name"
                  class="h-full w-full object-cover"
                />
                <LucideStethoscope v-else class="h-7 w-7 text-teal-600" />
              </div>

              <div class="space-y-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-mono text-xs font-bold text-gray-700 bg-white px-2.5 py-0.5 rounded-lg border border-gray-200 shadow-2xs">
                    {{ dashboardStore.patientSummary.upcoming_appointment.appointment_reference }}
                  </span>
                  <BaseStatusBadge :status="dashboardStore.patientSummary.upcoming_appointment.status" />
                </div>

                <h3 class="text-base sm:text-lg font-bold text-gray-900 leading-snug">
                  Dr. {{ dashboardStore.patientSummary.upcoming_appointment.doctor.user.name }}
                </h3>

                <p v-if="dashboardStore.patientSummary.upcoming_appointment.doctor.specialty" class="text-xs font-semibold text-teal-700 flex items-center gap-1.5">
                  <span class="inline-block h-1.5 w-1.5 rounded-full bg-teal-500" />
                  <span>{{ dashboardStore.patientSummary.upcoming_appointment.doctor.specialty.name }}</span>
                </p>
              </div>
            </div>

            <!-- Right: Schedule & Action CTA -->
            <div class="flex flex-col sm:flex-row md:flex-col lg:flex-row items-stretch sm:items-center md:items-end lg:items-center gap-3 shrink-0">
              <!-- Date & Time Capsule -->
              <div class="flex items-center gap-3.5 rounded-xl bg-white border border-slate-200/90 px-4 py-2.5 shadow-2xs">
                <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-700 shrink-0">
                  <LucideCalendar class="h-4 w-4" />
                </div>
                <div class="text-left">
                  <p class="text-xs font-bold text-gray-900">
                    {{ formatDate(dashboardStore.patientSummary.upcoming_appointment.scheduled_at) }}
                  </p>
                  <p class="text-[11px] font-semibold text-slate-500 font-mono flex items-center gap-1 mt-0.5">
                    <LucideClock class="h-3 w-3 text-slate-400" />
                    <span>{{ formatTime(dashboardStore.patientSummary.upcoming_appointment.scheduled_at) }}</span>
                  </p>
                </div>
              </div>

              <!-- Track Progress & Details CTA Button -->
              <NuxtLink
                :to="`/patient/appointments/${dashboardStore.patientSummary.upcoming_appointment.id}`"
                class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-primary-600 px-4 text-xs font-bold text-white hover:bg-primary-700 transition-colors shadow-2xs shrink-0"
              >
                <span>Track Live Progress</span>
                <LucideArrowRight class="h-3.5 w-3.5" />
              </NuxtLink>
            </div>
          </div>

          <!-- Progress Stepper in a Dedicated Clean Surface -->
          <div class="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-2xs">
            <FeaturesAppointmentsBookingProgressTracker
              :appointment="dashboardStore.patientSummary.upcoming_appointment"
              :compact="true"
              :show-logic-details="false"
            />
          </div>
        </div>
      </div>

      <!-- Quick Action Shortcuts -->
      <div class="space-y-4">
        <h2 class="text-lg font-bold text-gray-900">Quick Actions</h2>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 1. Book Appointment: Distinct Emerald/Teal Theme -->
          <NuxtLink
            to="/book"
            class="card card-hover group bg-emerald-50/30 border-emerald-200 hover:border-emerald-400"
          >
            <div class="h-10 w-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-3 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
              <LucideCalendarPlus class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">Book Appointment</h3>
            <p class="text-xs text-gray-500 mt-1">Schedule a consultation with our qualified specialists</p>
          </NuxtLink>

          <!-- 2. My Appointments: Distinct Purple/Violet Theme -->
          <NuxtLink
            to="/patient/appointments"
            class="card card-hover group bg-purple-50/30 border-purple-200 hover:border-purple-400"
          >
            <div class="h-10 w-10 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center mb-3 group-hover:bg-purple-600 group-hover:text-white transition-colors">
              <LucideCalendarCheck class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">My Appointments</h3>
            <p class="text-xs text-gray-500 mt-1">View booking history and consultation status</p>
          </NuxtLink>

          <!-- 3. AI Health Assistant: Distinct Sky/Blue Theme -->
          <NuxtLink
            to="/ai-assistant"
            class="card card-hover group bg-sky-50/30 border-sky-200 hover:border-sky-400"
          >
            <div class="h-10 w-10 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center mb-3 group-hover:bg-sky-600 group-hover:text-white transition-colors">
              <LucideBot class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">AI Health Assistant</h3>
            <p class="text-xs text-gray-500 mt-1">First-aid guidance & general health questions</p>
          </NuxtLink>

          <!-- 4. Browse Doctors: Distinct Amber/Gold Theme -->
          <NuxtLink
            to="/doctors"
            class="card card-hover group bg-amber-50/30 border-amber-200 hover:border-amber-400"
          >
            <div class="h-10 w-10 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center mb-3 group-hover:bg-amber-600 group-hover:text-white transition-colors">
              <LucideStethoscope class="h-5 w-5" />
            </div>
            <h3 class="font-bold text-gray-900 text-sm">Browse Doctors</h3>
            <p class="text-xs text-gray-500 mt-1">Find healthcare specialists and check availability</p>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
