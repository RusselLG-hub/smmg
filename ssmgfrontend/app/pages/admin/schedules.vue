<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useDoctorsStore } from '~/stores/doctors'
import { useSchedulesStore } from '~/stores/schedules'
import { WEEKDAYS } from '~~/shared/types/Schedule'

definePageMeta({
  middleware: 'auth',
})

const doctorsStore = useDoctorsStore()
const schedulesStore = useSchedulesStore()

const selectedDoctorId = ref<string>('')
const actionSuccess = ref<string | null>(null)
const actionError = ref<string | null>(null)
const showAddModal = ref(false)
const pendingDeleteId = ref<string | null>(null)
const deletingSchedule = ref(false)

const form = reactive({
  day_of_week: 0,
  start_time: '08:00',
  end_time: '17:00',
  slot_duration_minutes: 30,
  is_active: true,
})

onMounted(async () => {
  await doctorsStore.fetchDoctors(false)
  if (doctorsStore.doctors.length > 0) {
    selectedDoctorId.value = doctorsStore.doctors[0].id
  }
})

watch(selectedDoctorId, async (newId) => {
  if (newId) {
    await schedulesStore.fetchDoctorSchedules(newId)
  }
})

const handleCreateSchedule = async () => {
  actionError.value = null
  actionSuccess.value = null
  if (!selectedDoctorId.value) {
    actionError.value = 'Please select a doctor first'
    return
  }

  try {
    await schedulesStore.createSchedule({
      doctor_profile_id: selectedDoctorId.value,
      day_of_week: Number(form.day_of_week),
      start_time: form.start_time,
      end_time: form.end_time,
      slot_duration_minutes: Number(form.slot_duration_minutes),
      is_active: form.is_active,
    })
    actionSuccess.value = 'Working schedule added successfully'
    showAddModal.value = false
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to create schedule'
  }
}

const handleDeleteSchedule = async () => {
  if (!pendingDeleteId.value) return
  actionError.value = null
  actionSuccess.value = null
  deletingSchedule.value = true
  try {
    await schedulesStore.deleteSchedule(pendingDeleteId.value)
    actionSuccess.value = 'Schedule deleted'
    pendingDeleteId.value = null
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to delete schedule'
  } finally {
    deletingSchedule.value = false
  }
}

const handleToggleActive = async (id: string, currentActive: boolean) => {
  actionError.value = null
  actionSuccess.value = null
  try {
    await schedulesStore.updateSchedule(id, { is_active: !currentActive })
    actionSuccess.value = 'Schedule updated'
  } catch (err: any) {
    actionError.value = err?.data?.detail || 'Failed to update schedule'
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <BasePageHeader
      title="Doctor Working Schedules"
      description="Configure weekly working hours and slot durations for doctors"
    >
      <template #actions>
        <div class="w-full sm:w-72 text-left">
          <label class="form-label mb-1">Select Doctor Profile</label>
          <select
            v-model="selectedDoctorId"
            class="form-input w-full text-sm"
          >
            <option v-for="d in doctorsStore.doctors" :key="d.id" :value="d.id">
              Dr. {{ d.user.name }} ({{ d.specialty?.name || 'General' }})
            </option>
          </select>
        </div>
      </template>
    </BasePageHeader>

    <!-- Alert Notifications -->
    <div v-if="actionSuccess" class="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideCheckCircle2 class="h-5 w-5 text-green-500" />
        <span>{{ actionSuccess }}</span>
      </div>
      <button class="text-green-700 font-bold" @click="actionSuccess = null">&times;</button>
    </div>

    <div v-if="actionError" class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LucideAlertCircle class="h-5 w-5 text-red-500" />
        <span>{{ actionError }}</span>
      </div>
      <button class="text-red-700 font-bold" @click="actionError = null">&times;</button>
    </div>

    <!-- Main Content -->
    <BaseEmptyState
      v-if="!selectedDoctorId"
      title="No Doctor Selected"
    >
      <template #icon>
        <LucideCalendarOff class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <div v-else class="space-y-6">
      <div class="flex justify-between items-center card p-4">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-lg bg-primary-100 text-primary-600 flex items-center justify-center">
            <LucideClock class="h-5 w-5" />
          </div>
          <div>
            <h2 class="text-lg font-bold text-gray-900">Weekly Schedule</h2>
            <p class="text-xs text-gray-500">Recurring availability slots for selected doctor</p>
          </div>
        </div>

        <button
          class="btn btn-primary"
          @click="showAddModal = true"
        >
          <LucidePlus class="h-4 w-4" />
          <span>Add Working Hours</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="schedulesStore.loading" class="flex justify-center py-12">
        <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
      </div>

      <!-- Empty State -->
      <BaseEmptyState
        v-else-if="schedulesStore.schedules.length === 0"
        title="No Schedules Configured"
        description="Click 'Add Working Hours' to define doctor availability."
      >
        <template #icon>
          <LucideCalendarX class="h-10 w-10 text-gray-400" />
        </template>
      </BaseEmptyState>

      <!-- Schedule Table -->
      <div v-else class="card-table">
        <table class="w-full text-left text-sm text-gray-700">
          <thead class="bg-gray-50 border-b border-gray-200 text-gray-700 font-semibold">
            <tr>
              <th class="px-4 py-3">Day of Week</th>
              <th class="px-4 py-3">Working Time</th>
              <th class="px-4 py-3">Slot Duration</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="s in schedulesStore.schedules" :key="s.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-semibold text-gray-900">
                <span class="inline-block px-2.5 py-1 rounded bg-primary-50 text-primary-700 font-medium text-xs">
                  {{ WEEKDAYS[s.day_of_week] }}
                </span>
              </td>
              <td class="px-4 py-3 font-mono font-medium text-gray-800">
                {{ s.start_time }} &mdash; {{ s.end_time }}
              </td>
              <td class="px-4 py-3 text-gray-600">
                {{ s.slot_duration_minutes }} minutes
              </td>
              <td class="px-4 py-3">
                <button
                  class="px-2 py-0.5 rounded text-xs font-semibold cursor-pointer transition-colors"
                  :class="s.is_active ? 'bg-green-100 text-green-800 hover:bg-green-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                  @click="handleToggleActive(s.id, s.is_active)"
                >
                  {{ s.is_active ? 'Active' : 'Disabled' }}
                </button>
              </td>
              <td class="px-4 py-3 text-right">
                <button class="text-red-600 hover:text-red-800 text-xs font-medium" @click="pendingDeleteId = s.id">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL: ADD SCHEDULE -->
    <div v-if="showAddModal" class="modal-overlay" role="dialog" aria-modal="true" aria-label="Add working hours" @click.self="showAddModal = false">
      <div class="modal-panel max-w-md space-y-4">
        <h3 class="text-lg font-bold text-gray-900">Add Working Hours</h3>

        <form class="space-y-3" @submit.prevent="handleCreateSchedule">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Weekday</label>
            <select v-model="form.day_of_week" class="w-full px-3 py-2 border rounded-lg text-sm bg-white">
              <option v-for="(day, idx) in WEEKDAYS" :key="idx" :value="idx">{{ day }}</option>
            </select>
          </div>

          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Start Time (HH:MM)</label>
              <input v-model="form.start_time" type="time" required class="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">End Time (HH:MM)</label>
              <input v-model="form.end_time" type="time" required class="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Slot Duration</label>
            <select v-model="form.slot_duration_minutes" class="w-full px-3 py-2 border rounded-lg text-sm bg-white">
              <option :value="15">15 minutes</option>
              <option :value="20">20 minutes</option>
              <option :value="30">30 minutes</option>
              <option :value="45">45 minutes</option>
              <option :value="60">60 minutes</option>
            </select>
          </div>

          <div class="flex items-center gap-2 pt-2">
            <input id="is_active" v-model="form.is_active" type="checkbox" class="h-4 w-4 text-primary-600 rounded" />
            <label for="is_active" class="text-xs text-gray-700 font-medium">Enable schedule immediately</label>
          </div>

          <div class="modal-actions">
            <button type="button" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800" @click="showAddModal = false">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">Save Schedule</button>
          </div>
        </form>
      </div>
    </div>

    <BaseConfirmModal
      :model-value="Boolean(pendingDeleteId)"
      title="Delete working schedule?"
      description="Appointments can no longer be booked during this recurring schedule."
      confirm-label="Delete Schedule"
      :loading="deletingSchedule"
      @update:model-value="!$event && (pendingDeleteId = null)"
      @confirm="handleDeleteSchedule"
    />
  </div>
</template>
