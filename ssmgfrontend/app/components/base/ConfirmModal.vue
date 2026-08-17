<script setup lang="ts">
withDefaults(defineProps<{
  modelValue: boolean
  title: string
  description: string
  confirmLabel?: string
  loading?: boolean
}>(), {
  confirmLabel: 'Delete',
  loading: false,
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: boolean): void
  (event: 'confirm'): void
}>()
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    :title="title"
    :description="description"
    max-width="sm"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="flex gap-4 rounded-2xl border border-red-100 bg-red-50/70 p-4">
      <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-white text-red-600 shadow-sm ring-1 ring-red-100">
        <LucideTrash2 class="h-5 w-5" />
      </div>
      <div>
        <p class="text-sm font-semibold text-slate-900">This action cannot be undone</p>
        <p class="mt-1 text-sm leading-6 text-slate-600">The selected record will be permanently removed from SSMG.</p>
      </div>
    </div>

    <template #footer>
      <button type="button" class="btn btn-secondary" :disabled="loading" @click="emit('update:modelValue', false)">Cancel</button>
      <button type="button" class="btn btn-danger" :disabled="loading" @click="emit('confirm')">
        <LucideLoader2 v-if="loading" class="h-4 w-4 animate-spin" />
        <LucideTrash2 v-else class="h-4 w-4" />
        <span>{{ loading ? 'Deleting...' : confirmLabel }}</span>
      </button>
    </template>
  </BaseModal>
</template>
