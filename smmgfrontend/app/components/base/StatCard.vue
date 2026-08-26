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
    case 'success': return 'border-emerald-500 bg-emerald-50 text-emerald-700'
    case 'warning': return 'border-amber-500 bg-amber-50 text-amber-700'
    case 'danger': return 'border-rose-500 bg-rose-50 text-rose-700'
    case 'info': return 'border-blue-500 bg-blue-50 text-blue-700'
    case 'default':
    default: return 'border-slate-400 bg-slate-50 text-slate-700'
  }
})
</script>

<template>
  <div class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_8px_28px_rgba(30,64,175,0.06)] transition-all duration-300 hover:border-blue-200 hover:shadow-[0_12px_34px_rgba(30,64,175,0.1)]">
    <div class="flex items-center gap-4">
      <div v-if="$slots.icon" class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border-l-4 transition-transform duration-300 group-hover:scale-105" :class="variantClasses">
        <slot name="icon" />
      </div>
      <div class="min-w-0">
        <p class="text-xs font-bold uppercase tracking-[0.08em] text-slate-500">{{ label }}</p>
        <p class="mt-1 font-display text-3xl font-bold tracking-tight text-slate-950">{{ value }}</p>
      </div>
    </div>
  </div>
</template>
