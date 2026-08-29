<script setup lang="ts">
import type { Appointment } from '~~/shared/types/Appointment'

defineProps<{
  modelValue: boolean
  appointment: Appointment | null
}>()

defineEmits<{
  (event: 'update:modelValue', value: boolean): void
}>()
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Patient Information"
    :description="appointment ? `Appointment ${appointment.appointment_reference}` : undefined"
    max-width="lg"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="appointment" class="space-y-5">
      <div class="flex items-center gap-3 rounded-xl bg-primary-50 p-4">
        <div class="h-12 w-12 overflow-hidden rounded-full bg-white ring-1 ring-primary-200">
          <BaseAvatar :src="appointment.patient.profile_image_url" :alt="appointment.patient.user.name" />
        </div>
        <div><p class="font-bold text-gray-900">{{ appointment.patient.user.name }}</p><p class="text-sm text-gray-600">{{ appointment.patient.user.email }}</p></div>
      </div>
      <dl class="grid gap-4 text-sm sm:grid-cols-2">
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Phone</dt><dd class="mt-1 text-gray-900">{{ appointment.patient.phone || 'Not provided' }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Date of birth</dt><dd class="mt-1 text-gray-900">{{ appointment.patient.date_of_birth || 'Not provided' }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Gender</dt><dd class="mt-1 text-gray-900">{{ appointment.patient.gender || 'Not provided' }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Service</dt><dd class="mt-1 text-gray-900">{{ appointment.service?.name || 'General consultation' }}</dd></div>
        <div class="sm:col-span-2"><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Address</dt><dd class="mt-1 text-gray-900">{{ appointment.patient.address || 'Not provided' }}</dd></div>
        <div class="sm:col-span-2"><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Reason for visit</dt><dd class="mt-1 whitespace-pre-wrap text-gray-900">{{ appointment.reason || 'Not provided' }}</dd></div>
      </dl>
    </div>
  </BaseModal>
</template>
