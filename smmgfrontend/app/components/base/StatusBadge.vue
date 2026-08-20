<script setup lang="ts">
interface Props {
  status: string
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'sm',
})

const statusConfig = computed(() => {
  const s = props.status.toLowerCase()
  switch (s) {
    case 'pending':
      return { bg: 'bg-amber-50', text: 'text-amber-700', ring: 'ring-amber-600/20' }
    case 'confirmed':
    case 'active':
    case 'verified':
      return { bg: 'bg-green-50', text: 'text-green-700', ring: 'ring-green-600/20' }
    case 'completed':
      return { bg: 'bg-blue-50', text: 'text-blue-700', ring: 'ring-blue-600/20' }
    case 'cancelled':
      return { bg: 'bg-red-50', text: 'text-red-700', ring: 'ring-red-600/20' }
    case 'inactive':
    case 'deactivated':
    case 'unverified':
      return { bg: 'bg-gray-50', text: 'text-gray-600', ring: 'ring-gray-500/10' }
    default:
      return { bg: 'bg-gray-50', text: 'text-gray-600', ring: 'ring-gray-500/10' }
  }
})

const sizeClasses = computed(() => {
  return props.size === 'md' ? 'px-2.5 py-1 text-xs' : 'px-2 py-0.5 text-xs'
})

const displayText = computed(() => {
  const s = props.status
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase()
})
</script>

<template>
  <span
    class="inline-flex items-center rounded-md font-medium ring-1 ring-inset"
    :class="[statusConfig.bg, statusConfig.text, statusConfig.ring, sizeClasses]"
  >
    {{ displayText }}
  </span>
</template>
