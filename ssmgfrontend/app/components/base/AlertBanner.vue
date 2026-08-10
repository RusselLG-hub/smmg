<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  dismissible?: boolean
}>(), {
  dismissible: true
})

const emit = defineEmits<{
  (e: 'dismiss'): void
}>()

const typeClasses = computed(() => {
  switch (props.type) {
    case 'success': return 'bg-green-50 border-green-200 text-green-800'
    case 'error': return 'bg-red-50 border-red-200 text-red-800'
    case 'warning': return 'bg-amber-50 border-amber-200 text-amber-800'
    case 'info': return 'bg-blue-50 border-blue-200 text-blue-800'
    default: return 'bg-gray-50 border-gray-200 text-gray-800'
  }
})

const iconColor = computed(() => {
  switch (props.type) {
    case 'success': return 'text-green-500'
    case 'error': return 'text-red-500'
    case 'warning': return 'text-amber-500'
    case 'info': return 'text-blue-500'
    default: return 'text-gray-500'
  }
})
</script>

<template>
  <div class="flex items-start sm:items-center justify-between gap-3 px-4 py-3 rounded-lg border text-sm" :class="typeClasses" role="alert">
    <div class="flex items-start sm:items-center gap-3">
      <LucideCheckCircle2 v-if="type === 'success'" class="h-5 w-5 shrink-0 mt-0.5 sm:mt-0" :class="iconColor" />
      <LucideAlertCircle v-else-if="type === 'error'" class="h-5 w-5 shrink-0 mt-0.5 sm:mt-0" :class="iconColor" />
      <LucideAlertTriangle v-else-if="type === 'warning'" class="h-5 w-5 shrink-0 mt-0.5 sm:mt-0" :class="iconColor" />
      <LucideInfo v-else class="h-5 w-5 shrink-0 mt-0.5 sm:mt-0" :class="iconColor" />
      <span>{{ message }}</span>
    </div>
    <button v-if="dismissible" type="button" class="shrink-0 p-1 rounded-md opacity-70 hover:opacity-100 transition-opacity focus:outline-none focus:ring-2 focus:ring-current" @click="emit('dismiss')">
      <span class="sr-only">Dismiss</span>
      <LucideX class="h-4 w-4" />
    </button>
  </div>
</template>
