<script setup lang="ts">
import { computed } from 'vue'
import type { Appointment } from '~~/shared/types/Appointment'

const props = withDefaults(
  defineProps<{
    appointment: Appointment
    compact?: boolean
    showLogicDetails?: boolean
  }>(),
  {
    compact: false,
    showLogicDetails: true,
  },
)

const isCancelled = computed(() => props.appointment.status === 'cancelled')
const isCompleted = computed(() => props.appointment.status === 'completed')
const isConfirmed = computed(() => props.appointment.status === 'confirmed')
const isPending = computed(() => props.appointment.status === 'pending')

// Determine active step index: 0 = Submitted, 1 = Clinic Review, 2 = Confirmed, 3 = Completed
const currentStepIndex = computed(() => {
  if (isCancelled.value) return 1 // Stuck/stopped at review or cancellation
  if (isCompleted.value) return 3
  if (isConfirmed.value) return 2
  return 1 // Pending is at step 1 (Clinic Review & Approval)
})

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

const steps = computed(() => [
  {
    id: 'submitted',
    name: 'Submitted',
    label: 'Request Booked',
    description: 'Appointment request submitted by patient',
    icon: 'LucideClock',
  },
  {
    id: 'reviewing',
    name: 'Clinic Review',
    label: 'Staff Approval',
    description: 'Awaiting confirmation by Clinic Staff / Doctor Assistant',
    icon: 'LucideUserCheck',
  },
  {
    id: 'confirmed',
    name: 'Confirmed',
    label: 'Slot Locked',
    description: 'Schedule confirmed by clinic',
    icon: 'LucideCalendarCheck',
  },
  {
    id: 'completed',
    name: 'Completed',
    label: 'Consultation Done',
    description: 'Consultation conducted by attending doctor',
    icon: 'LucideCheckCircle2',
  },
])
</script>

<template>
  <!-- COMPACT PROGRESS TRACKER (FOR LIST CARDS & DASHBOARD) -->
  <div v-if="compact" class="space-y-3">
    <div class="flex items-center justify-between text-xs mb-1">
      <span class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Booking Status</span>
      <span
        v-if="isCancelled"
        class="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-0.5 text-xs font-semibold text-red-700 border border-red-200"
      >
        <LucideXCircle class="h-3.5 w-3.5" />
        Cancelled
      </span>
      <span
        v-else-if="isPending"
        class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 border border-amber-200 animate-pulse"
      >
        <LucideClock class="h-3.5 w-3.5 text-amber-600" />
        Awaiting Staff Review
      </span>
      <span
        v-else-if="isConfirmed"
        class="inline-flex items-center gap-1 rounded-full bg-teal-50 px-2.5 py-0.5 text-xs font-semibold text-teal-700 border border-teal-200"
      >
        <LucideCheckCircle2 class="h-3.5 w-3.5 text-teal-600" />
        Confirmed by Clinic
      </span>
      <span
        v-else-if="isCompleted"
        class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 border border-blue-200"
      >
        <LucideCheckCircle2 class="h-3.5 w-3.5 text-blue-600" />
        Consultation Completed
      </span>
    </div>

    <!-- Stepper bar -->
    <div class="relative flex items-center justify-between">
      <!-- Background Connecting Line (Centered with the h-6 dots at top-3) -->
      <div class="absolute left-3 right-3 top-3 h-0.5 -translate-y-1/2 bg-gray-200" aria-hidden="true" />
      <!-- Active Filled Progress Line (Centered with the h-6 dots at top-3) -->
      <div
        class="absolute left-3 top-3 h-0.5 -translate-y-1/2 transition-all duration-500"
        :class="isCancelled ? 'bg-red-400' : isConfirmed ? 'bg-teal-600' : 'bg-primary-600'"
        :style="{
          width: isCancelled
            ? 'calc((100% - 24px) * 0.3333)'
            : currentStepIndex === 1
            ? 'calc((100% - 24px) * 0.3333)'
            : currentStepIndex === 2
            ? 'calc((100% - 24px) * 0.6667)'
            : currentStepIndex === 3
            ? 'calc(100% - 24px)'
            : '0px',
        }"
        aria-hidden="true"
      />

      <!-- Steps Dots -->
      <div
        v-for="(step, idx) in steps"
        :key="step.id"
        class="relative z-10 flex flex-col items-center"
      >
        <div
          class="flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold transition-all"
          :class="[
            isCancelled && idx === 1
              ? 'bg-red-500 text-white ring-2 ring-red-200'
              : idx < currentStepIndex
              ? 'bg-teal-600 text-white ring-2 ring-teal-100'
              : idx === currentStepIndex
              ? isPending
                ? 'bg-amber-500 text-white ring-4 ring-amber-100'
                : isConfirmed
                ? 'bg-teal-600 text-white ring-4 ring-teal-100'
                : 'bg-primary-600 text-white ring-4 ring-primary-100'
              : 'bg-white text-gray-400 border-2 border-gray-300',
          ]"
        >
          <LucideX v-if="isCancelled && idx === 1" class="h-3.5 w-3.5 stroke-[3]" />
          <LucideClock v-else-if="idx === 1 && isPending" class="h-3.5 w-3.5" />
          <LucideCheck v-else-if="idx <= currentStepIndex && !isCancelled" class="h-3.5 w-3.5 stroke-[3]" />
          <span v-else>{{ idx + 1 }}</span>
        </div>
        <span
          class="mt-1.5 text-[11px] whitespace-nowrap transition-colors"
          :class="[
            idx === currentStepIndex
              ? isCancelled
                ? 'font-bold text-red-600'
                : isPending
                ? 'font-bold text-amber-700'
                : 'font-bold text-teal-800'
              : idx < currentStepIndex
              ? 'font-medium text-gray-700'
              : 'font-medium text-gray-400',
          ]"
        >
          {{ step.name }}
        </span>
      </div>
    </div>
  </div>

  <!-- FULL DETAILED PROGRESS CARD (FOR APPOINTMENT DETAILS PAGE) -->
  <div v-else class="space-y-6">
    <!-- Card Container -->
    <div class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
      <!-- Section Header -->
      <div class="flex flex-col gap-2 border-b border-gray-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span class="inline-flex items-center gap-1.5 rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-semibold text-primary-700">
            <LucideActivity class="h-3.5 w-3.5" />
            Service Progress
          </span>
          <h2 class="mt-1.5 text-xl font-bold text-gray-900">
            Appointment Booking Lifecycle
          </h2>
          <p class="text-xs text-gray-500">
            Track your appointment verification, staff confirmation, and consultation status
          </p>
        </div>

        <!-- Reference & Status Pill -->
        <div class="flex flex-wrap items-center gap-2">
          <span class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-1 font-mono text-xs font-bold text-gray-700">
            Ref: {{ appointment.appointment_reference }}
          </span>
          <BaseStatusBadge :status="appointment.status" />
        </div>
      </div>

      <!-- Cancelled Alert Banner -->
      <div
        v-if="isCancelled"
        class="mt-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-800"
      >
        <LucideAlertCircle class="h-5 w-5 shrink-0 text-red-600 mt-0.5" />
        <div>
          <h3 class="text-sm font-bold">This appointment has been cancelled</h3>
          <p v-if="appointment.cancellation_reason" class="mt-1 text-xs text-red-700">
            <strong class="font-semibold">Reason provided:</strong> {{ appointment.cancellation_reason }}
          </p>
          <p v-else class="mt-1 text-xs text-red-700">
            This appointment was cancelled prior to the scheduled consultation.
          </p>
        </div>
      </div>

      <!-- Live Stepper Flow -->
      <div class="mt-8 px-2">
        <div class="relative">
          <!-- Desktop/Tablet Stepper -->
          <div class="hidden sm:block">
            <!-- Background Line -->
            <div class="absolute left-10 right-10 top-6 h-1 -translate-y-1/2 bg-gray-200" aria-hidden="true" />
            <!-- Active Fill Line -->
            <div
              class="absolute left-10 top-6 h-1 -translate-y-1/2 transition-all duration-700"
              :class="isCancelled ? 'bg-red-400' : 'bg-primary-600'"
              :style="{
                width: isCancelled
                  ? '33%'
                  : currentStepIndex === 1
                  ? '33%'
                  : currentStepIndex === 2
                  ? '66%'
                  : currentStepIndex === 3
                  ? '100%'
                  : '0%',
              }"
              aria-hidden="true"
            />

            <!-- Steps -->
            <div class="relative z-10 grid grid-cols-4 gap-2 text-center">
              <div v-for="(step, idx) in steps" :key="step.id" class="flex flex-col items-center">
                <!-- Step Circle -->
                <div
                  class="flex h-12 w-12 items-center justify-center rounded-full text-base font-bold shadow-sm transition-all"
                  :class="[
                    isCancelled && idx === 1
                      ? 'bg-red-600 text-white ring-4 ring-red-100'
                      : idx < currentStepIndex
                      ? 'bg-primary-600 text-white ring-4 ring-primary-100'
                      : idx === currentStepIndex
                      ? isPending
                        ? 'bg-amber-500 text-white ring-4 ring-amber-100 animate-pulse'
                        : 'bg-primary-600 text-white ring-4 ring-primary-100'
                      : 'border-2 border-gray-300 bg-white text-gray-400',
                  ]"
                >
                  <LucideCheck v-if="idx < currentStepIndex && !isCancelled" class="h-6 w-6 stroke-[2.5]" />
                  <LucideX v-else-if="isCancelled && idx === 1" class="h-6 w-6 stroke-[2.5]" />
                  <LucideClock v-else-if="idx === 1 && isPending" class="h-6 w-6" />
                  <LucideCalendarCheck v-else-if="idx === 2 && isConfirmed" class="h-6 w-6" />
                  <LucideCheckCircle2 v-else-if="idx === 3 && isCompleted" class="h-6 w-6" />
                  <span v-else>{{ idx + 1 }}</span>
                </div>

                <!-- Label & Info -->
                <div class="mt-3">
                  <p
                    class="text-xs font-bold"
                    :class="[
                      isCancelled && idx === 1
                        ? 'text-red-700'
                        : idx <= currentStepIndex
                        ? 'text-gray-900'
                        : 'text-gray-400',
                    ]"
                  >
                    {{ step.name }}
                  </p>
                  <p
                    class="mt-0.5 text-[11px]"
                    :class="[
                      isCancelled && idx === 1
                        ? 'text-red-600 font-semibold'
                        : idx === currentStepIndex && isPending
                        ? 'text-amber-700 font-semibold'
                        : idx <= currentStepIndex
                        ? 'text-gray-600'
                        : 'text-gray-400',
                    ]"
                  >
                    {{ isCancelled && idx === 1 ? 'Cancelled' : step.label }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Mobile Vertical Stepper -->
          <div class="space-y-6 sm:hidden">
            <div
              v-for="(step, idx) in steps"
              :key="step.id"
              class="relative flex items-start gap-4"
            >
              <!-- Connecting Line -->
              <div
                v-if="idx < steps.length - 1"
                class="absolute left-5 top-10 bottom-0 w-0.5 -ml-px"
                :class="idx < currentStepIndex ? 'bg-primary-600' : 'bg-gray-200'"
                aria-hidden="true"
              />

              <!-- Icon Circle -->
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold shadow-sm"
                :class="[
                  isCancelled && idx === 1
                    ? 'bg-red-600 text-white ring-2 ring-red-200'
                    : idx < currentStepIndex
                    ? 'bg-primary-600 text-white ring-2 ring-primary-100'
                    : idx === currentStepIndex
                    ? isPending
                      ? 'bg-amber-500 text-white ring-2 ring-amber-100'
                      : 'bg-primary-600 text-white ring-2 ring-primary-100'
                    : 'border-2 border-gray-300 bg-white text-gray-400',
                ]"
              >
                <LucideCheck v-if="idx < currentStepIndex && !isCancelled" class="h-5 w-5 stroke-[2.5]" />
                <LucideX v-else-if="isCancelled && idx === 1" class="h-5 w-5" />
                <LucideClock v-else-if="idx === 1 && isPending" class="h-5 w-5" />
                <LucideCalendarCheck v-else-if="idx === 2 && isConfirmed" class="h-5 w-5" />
                <LucideCheckCircle2 v-else-if="idx === 3 && isCompleted" class="h-5 w-5" />
                <span v-else>{{ idx + 1 }}</span>
              </div>

              <!-- Step Info -->
              <div class="pt-1">
                <div class="flex items-center gap-2">
                  <h4
                    class="text-sm font-bold"
                    :class="idx <= currentStepIndex ? 'text-gray-900' : 'text-gray-400'"
                  >
                    {{ step.name }}
                  </h4>
                  <span
                    v-if="idx === currentStepIndex && isPending"
                    class="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-bold text-amber-800"
                  >
                    Active
                  </span>
                  <span
                    v-else-if="idx === currentStepIndex && isConfirmed"
                    class="rounded bg-teal-100 px-1.5 py-0.5 text-[10px] font-bold text-teal-800"
                  >
                    Active
                  </span>
                </div>
                <p class="mt-0.5 text-xs text-gray-500">{{ step.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Stage Explanatory Box -->
      <div class="mt-8 rounded-xl border p-4 sm:p-5" :class="[
        isCancelled
          ? 'border-red-200 bg-red-50/60'
          : isPending
          ? 'border-amber-200 bg-amber-50/60'
          : isConfirmed
          ? 'border-teal-200 bg-teal-50/60'
          : 'border-blue-200 bg-blue-50/60'
      ]">
        <div class="flex items-start gap-3">
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
            :class="[
              isCancelled
                ? 'bg-red-100 text-red-700'
                : isPending
                ? 'bg-amber-100 text-amber-800'
                : isConfirmed
                ? 'bg-teal-100 text-teal-800'
                : 'bg-blue-100 text-blue-800'
            ]"
          >
            <LucideClock v-if="isPending" class="h-4 w-4" />
            <LucideCalendarCheck v-else-if="isConfirmed" class="h-4 w-4" />
            <LucideCheckCircle2 v-else-if="isCompleted" class="h-4 w-4" />
            <LucideXCircle v-else class="h-4 w-4" />
          </div>

          <div class="space-y-1 text-xs">
            <p class="font-bold text-gray-900">
              <span v-if="isPending">Stage 2 of 4: Clinic Review & Verification in Progress</span>
              <span v-else-if="isConfirmed">Stage 3 of 4: Appointment Confirmed & Locked</span>
              <span v-else-if="isCompleted">Stage 4 of 4: Healthcare Consultation Completed</span>
              <span v-else>Appointment Workflow Terminated</span>
            </p>

            <p v-if="isPending" class="text-gray-700 leading-relaxed">
              Your consultation request is pending confirmation. <strong>Clinic Staff</strong> or the <strong>Doctor's Assistant</strong> (or attending doctor) will review and confirm your reserved time slot. You will receive an automated email notification as soon as the appointment is confirmed.
            </p>
            <p v-else-if="isConfirmed" class="text-gray-700 leading-relaxed">
              Your consultation has been officially confirmed by clinic staff. Dr. {{ appointment.doctor.user.name }} is scheduled to see you on <strong>{{ formatDate(appointment.scheduled_at) }}</strong> at <strong>{{ formatTime(appointment.scheduled_at) }}</strong>. Please arrive 10 minutes early.
            </p>
            <p v-else-if="isCompleted" class="text-gray-700 leading-relaxed">
              This appointment has been fulfilled and completed by Dr. {{ appointment.doctor.user.name }}. You can review your consultation records in your patient history.
            </p>
            <p v-else class="text-gray-700 leading-relaxed">
              This appointment has been cancelled. If you still require medical consultation, please book a new appointment or contact our clinic staff.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- BUSINESS LOGIC & APPROVAL RULES ACCORDION / CARD -->
    <div
      v-if="showLogicDetails"
      class="rounded-2xl border border-gray-200 bg-gray-50/70 p-6 sm:p-7 space-y-4"
    >
      <div class="flex items-center gap-2 text-gray-900 font-bold text-sm">
        <LucideInfo class="h-4 w-4 text-primary-600" />
        <span>How Clinic Booking & Approvals Work</span>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 text-xs text-gray-600">
        <div class="rounded-xl border border-gray-200 bg-white p-4 space-y-1.5 shadow-sm">
          <div class="flex items-center gap-2 font-semibold text-gray-900">
            <LucideUserCheck class="h-4 w-4 text-teal-600" />
            <span>Who Approves Your Booking?</span>
          </div>
          <p class="leading-relaxed text-gray-600">
            Appointments submitted by patients are queued for approval by <strong>Clinic Staff / Doctor's Assistants</strong> or the <strong>Attending Doctor</strong>. They verify doctor availability and clinic room scheduling before confirming.
          </p>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white p-4 space-y-1.5 shadow-sm">
          <div class="flex items-center gap-2 font-semibold text-gray-900">
            <LucideMail class="h-4 w-4 text-teal-600" />
            <span>Automatic Notifications</span>
          </div>
          <p class="leading-relaxed text-gray-600">
            You receive instant email confirmations when your booking is submitted, when staff confirms it, and if any rescheduling or cancellation occurs.
          </p>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white p-4 space-y-1.5 shadow-sm">
          <div class="flex items-center gap-2 font-semibold text-gray-900">
            <LucideCalendarClock class="h-4 w-4 text-teal-600" />
            <span>24-Hour Policy</span>
          </div>
          <p class="leading-relaxed text-gray-600">
            Patients can reschedule or cancel appointments freely up to <strong>24 hours</strong> before the scheduled consultation time. Within 24 hours, cancellations require direct clinic staff assistance.
          </p>
        </div>

        <div class="rounded-xl border border-gray-200 bg-white p-4 space-y-1.5 shadow-sm">
          <div class="flex items-center gap-2 font-semibold text-gray-900">
            <LucideRefreshCw class="h-4 w-4 text-teal-600" />
            <span>Rescheduling Workflow</span>
          </div>
          <p class="leading-relaxed text-gray-600">
            If you reschedule an appointment, it temporarily returns to <strong>Pending</strong> status so clinic staff can re-verify the new time slot with the doctor's schedule.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
