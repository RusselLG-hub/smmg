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
    case 'success': return 'bg-emerald-50 text-emerald-600 ring-emerald-100'
    case 'warning': return 'bg-amber-50 text-amber-600 ring-amber-100'
    case 'danger': return 'bg-rose-50 text-rose-600 ring-rose-100'
    case 'info': return 'bg-blue-50 text-blue-600 ring-blue-100'
    case 'default':
    default: return 'bg-slate-50 text-slate-600 ring-slate-100'
  }
})
</script>

<template>
  <div class="group relative overflow-hidden rounded-2xl border border-white/80 bg-white p-5 shadow-sm ring-1 ring-slate-200/70 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
    <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary-500 to-teal-500 opacity-70" />
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-slate-500">{{ label }}</p>
        <p class="mt-2 text-3xl font-bold tracking-tight text-slate-950">{{ value }}</p>
      </div>
      <div v-if="$slots.icon" class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ring-1 transition-transform duration-300 group-hover:scale-105" :class="variantClasses">
        <slot name="icon" />
      </div>
    </div>
  </div>
</template>
