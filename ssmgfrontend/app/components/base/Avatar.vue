<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  src?: string | null
  alt: string
}>(), {
  src: null,
})

const fallback = '/images/default-avatar.svg'
const imageSrc = ref(props.src || fallback)

watch(() => props.src, (value) => {
  imageSrc.value = value || fallback
})

const useFallback = () => {
  imageSrc.value = fallback
}
</script>

<template>
  <img :src="imageSrc" :alt="alt" class="h-full w-full object-cover" @error="useFallback" />
</template>
