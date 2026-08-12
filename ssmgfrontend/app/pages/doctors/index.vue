<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useDoctorsStore } from '~/stores/doctors'
import { useSpecialtiesStore } from '~/stores/specialties'

const doctorsStore = useDoctorsStore()
const specialtiesStore = useSpecialtiesStore()

const selectedSpecialty = ref<string>('')

onMounted(async () => {
  await Promise.all([
    specialtiesStore.fetchSpecialties(true),
    doctorsStore.fetchDoctors(true),
  ])
})

watch(selectedSpecialty, async (newVal) => {
  await doctorsStore.fetchDoctors(true, newVal || undefined)
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <BasePageHeader
      title="Find a Doctor"
      description="Browse our qualified medical specialists"
    >
      <template #actions>
        <div class="w-full sm:w-64 text-left">
          <select
            v-model="selectedSpecialty"
            class="form-input w-full text-sm"
          >
            <option value="">All Specialties</option>
            <option
              v-for="s in specialtiesStore.specialties"
              :key="s.id"
              :value="s.id"
            >
              {{ s.name }}
            </option>
          </select>
        </div>
      </template>
    </BasePageHeader>

    <!-- Loading State -->
    <div v-if="doctorsStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <!-- Empty State -->
    <BaseEmptyState
      v-else-if="doctorsStore.doctors.length === 0"
      title="No Doctors Found"
      description="Try selecting a different specialty filter."
    >
      <template #icon>
        <LucideUserX class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <!-- Doctors Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="doc in doctorsStore.doctors"
        :key="doc.id"
        class="card card-hover !p-0 overflow-hidden flex flex-col"
      >
        <div class="p-6 flex-1 flex flex-col">
          <div class="flex items-start gap-4 mb-4">
            <div class="h-16 w-16 rounded-full overflow-hidden bg-primary-50 border border-primary-200 flex items-center justify-center shrink-0">
              <img v-if="doc.profile_image_url" :src="doc.profile_image_url" :alt="doc.user.name" class="h-full w-full object-cover" />
              <LucideStethoscope v-else class="h-8 w-8 text-primary-600" />
            </div>

            <div>
              <span v-if="doc.title" class="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-primary-100 text-primary-800 mb-1">
                {{ doc.title }}
              </span>
              <h3 class="text-lg font-bold text-gray-900">Dr. {{ doc.user.name }}</h3>
              <p v-if="doc.specialty" class="text-sm text-teal-600 font-medium flex items-center gap-1">
                <LucideActivity class="h-3.5 w-3.5" />
                {{ doc.specialty.name }}
              </p>
            </div>
          </div>

          <p v-if="doc.bio" class="text-sm text-gray-600 line-clamp-3 mb-4 flex-1">
            {{ doc.bio }}
          </p>
          <p v-else class="text-sm text-gray-400 italic mb-4 flex-1">
            No biography provided.
          </p>

          <div v-if="doc.phone" class="text-xs text-gray-500 flex items-center gap-1.5 pt-3 border-t border-gray-100">
            <LucidePhone class="h-3.5 w-3.5 text-gray-400" />
            <span>{{ doc.phone }}</span>
          </div>
        </div>

        <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex justify-end">
          <NuxtLink
            :to="`/doctors/${doc.id}`"
            class="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            <span>View Doctor Profile</span>
            <LucideChevronRight class="h-4 w-4" />
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
