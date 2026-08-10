<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center bg-white rounded-lg border border-gray-200 shadow-sm">
    <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
      <slot name="icon">
        <LucideInbox class="h-8 w-8 text-gray-400" />
      </slot>
    </div>
    <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
    <p v-if="description" class="mt-1.5 text-sm text-gray-500 max-w-md mx-auto">{{ description }}</p>
    <div v-if="$slots.action" class="mt-6">
      <slot name="action" />
    </div>
  </div>
</template>
