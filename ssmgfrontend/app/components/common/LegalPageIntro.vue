<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description: string }>()
</script>

<template>
  <div class="border-b border-primary-100 bg-primary-50">
    <div class="mx-auto max-w-4xl px-4 py-14 sm:px-6 sm:py-20 lg:px-8">
      <p class="text-sm font-bold uppercase tracking-widest text-primary-700">{{ eyebrow }}</p>
      <h1 class="mt-3 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">{{ title }}</h1>
      <p class="mt-5 max-w-2xl text-lg leading-8 text-gray-600">{{ description }}</p>
      <p class="mt-6 text-sm font-medium text-gray-500">Last updated: August 10, 2026</p>
    </div>
  </div>
</template>
