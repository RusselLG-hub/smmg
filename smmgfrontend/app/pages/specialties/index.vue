<script setup lang="ts">
import { onMounted } from 'vue'
import { useSpecialtiesStore } from '~/stores/specialties'

const specialtiesStore = useSpecialtiesStore()

onMounted(async () => {
  await specialtiesStore.fetchSpecialties(true)
})
</script>

<template>
  <div class="page-container">
    <BasePageHeader
      title="Medical Specialties"
      description="Explore available healthcare departments and fields"
    />

    <div v-if="specialtiesStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <BaseEmptyState
      v-else-if="specialtiesStore.specialties.length === 0"
      title="No Specialties Available"
    >
      <template #icon>
        <LucideActivity class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="s in specialtiesStore.specialties"
        :key="s.id"
        class="card card-hover flex flex-col"
      >
        <div class="flex items-center gap-3 mb-3">
          <div class="h-10 w-10 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
            <LucideAward class="h-5 w-5" />
          </div>
          <h3 class="text-xl font-bold text-gray-900">{{ s.name }}</h3>
        </div>

        <p v-if="s.description" class="text-sm text-gray-600 leading-relaxed mb-4 flex-1">
          {{ s.description }}
        </p>
        <p v-else class="text-sm text-gray-400 italic mb-4 flex-1">
          No description available.
        </p>

        <div class="pt-3 border-t border-gray-100 flex justify-between items-center text-xs">
          <NuxtLink
            :to="`/doctors?specialty_id=${s.id}`"
            class="font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1"
          >
            <span>View Doctors</span>
            <LucideArrowRight class="h-3.5 w-3.5" />
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
