<script setup lang="ts">
import { computed, onBeforeUnmount, useId, watch } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: boolean
  title: string
  description?: string
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl'
}>(), {
  maxWidth: 'md'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()
const titleId = `modal-title-${useId()}`

const close = () => {
  emit('update:modelValue', false)
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.modelValue) close()
}

watch(() => props.modelValue, (isOpen) => {
  if (!import.meta.client) return
  document.body.classList.toggle('overflow-hidden', isOpen)
  if (isOpen) window.addEventListener('keydown', handleKeydown)
  else window.removeEventListener('keydown', handleKeydown)
}, { immediate: true })

onBeforeUnmount(() => {
  if (!import.meta.client) return
  document.body.classList.remove('overflow-hidden')
  window.removeEventListener('keydown', handleKeydown)
})

const maxWidthClass = computed(() => {
  switch (props.maxWidth) {
    case 'sm': return 'max-w-sm'
    case 'lg': return 'max-w-lg'
    case 'xl': return 'max-w-xl'
    case 'md':
    default: return 'max-w-md'
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-6" :aria-labelledby="titleId" role="dialog" aria-modal="true">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="close"></div>

        <!-- Modal panel -->
        <Transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          enter-to-class="opacity-100 translate-y-0 sm:scale-100"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100 translate-y-0 sm:scale-100"
          leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        >
          <div v-if="modelValue" class="relative flex max-h-[92dvh] w-full flex-col overflow-hidden rounded-t-3xl border border-white/70 bg-white shadow-2xl sm:max-h-[90vh] sm:rounded-3xl" :class="maxWidthClass">
            
            <!-- Header -->
            <div class="flex shrink-0 items-start justify-between gap-4 border-b border-slate-200 bg-gradient-to-r from-primary-50 to-teal-50 px-5 py-4 sm:px-6">
              <div class="min-w-0">
                <h3 :id="titleId" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
                <p v-if="description" class="mt-1 text-sm text-gray-500">{{ description }}</p>
              </div>
              <button type="button" class="-mr-2 flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700" @click="close">
                <span class="sr-only">Close panel</span>
                <LucideX class="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            <!-- Body -->
            <div class="overflow-y-auto px-5 py-5 sm:px-6">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="flex shrink-0 flex-col-reverse gap-3 border-t border-slate-200 bg-slate-50/90 px-5 py-4 sm:flex-row sm:justify-end sm:px-6 [&>*]:min-h-11 [&>*]:w-full sm:[&>*]:w-auto">
              <slot name="footer" />
            </div>
            
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
