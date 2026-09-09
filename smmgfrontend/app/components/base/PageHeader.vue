<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  kicker?: string
}>()
</script>

<template>
  <div class="relative mb-8 overflow-hidden rounded-3xl border border-primary-100 bg-gradient-to-br from-white via-primary-50/70 to-teal-50 p-6 shadow-sm sm:p-8">
    <div class="absolute -right-12 -top-16 h-44 w-44 rounded-full bg-teal-200/30 blur-2xl" aria-hidden="true" />
    <div class="relative flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
      <div class="max-w-3xl">
        <p class="section-label">{{ kicker || 'SMMG Healthcare' }}</p>
        <h1 class="mt-2 text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">{{ title }}</h1>
        <p v-if="description" class="mt-2 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="flex flex-col gap-3 sm:flex-row sm:items-center">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>
