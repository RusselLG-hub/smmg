<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  src?: string | null
  alt: string
  fallback?: string
}>(), {
  src: null,
  fallback: '/images/default-avatar.svg',
})

const imageSrc = ref(props.src || props.fallback)

watch(() => props.src, (value) => {
  imageSrc.value = value || props.fallback
})

const useFallback = () => {
  imageSrc.value = props.fallback
}
</script>

<template>
  <img :src="imageSrc" :alt="alt" class="h-full w-full object-cover" @error="useFallback" />
</template>
