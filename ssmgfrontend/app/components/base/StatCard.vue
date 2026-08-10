<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  label: string
  value: string | number
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
}>(), {
  variant: 'default'
})

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'success': return 'bg-green-50 text-green-600'
    case 'warning': return 'bg-amber-50 text-amber-600'
    case 'danger': return 'bg-red-50 text-red-600'
    case 'info': return 'bg-blue-50 text-blue-600'
    case 'default':
    default: return 'bg-gray-100 text-gray-600'
  }
})
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-500">{{ label }}</p>
        <p class="mt-1.5 text-2xl font-semibold text-gray-900">{{ value }}</p>
      </div>
      <div v-if="$slots.icon" class="h-12 w-12 rounded-lg flex items-center justify-center shrink-0" :class="variantClasses">
        <slot name="icon" />
      </div>
    </div>
  </div>
</template>
