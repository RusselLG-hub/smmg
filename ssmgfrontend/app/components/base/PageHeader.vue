<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
    <div>
      <h1 class="text-2xl font-semibold text-gray-900">{{ title }}</h1>
      <p v-if="description" class="mt-1 text-sm text-gray-600">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="flex flex-col sm:flex-row sm:items-center gap-3">
      <slot name="actions" />
    </div>
  </div>
</template>
