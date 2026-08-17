<script setup lang="ts">
import { onMounted } from 'vue'
import { useClinicServicesStore } from '~/stores/clinicServices'

const clinicServicesStore = useClinicServicesStore()

onMounted(async () => {
  await clinicServicesStore.fetchServices(true)
})
</script>

<template>
  <div class="page-container">
    <BasePageHeader
      title="Clinic & Hospital Services"
      description="Discover comprehensive healthcare treatments and clinical offerings"
    />

    <div v-if="clinicServicesStore.loading" class="flex justify-center py-16">
      <LucideLoader2 class="h-8 w-8 text-primary-600 animate-spin" />
    </div>

    <BaseEmptyState
      v-else-if="clinicServicesStore.services.length === 0"
      title="No Services Available"
    >
      <template #icon>
        <LucideHeartHandshake class="h-10 w-10 text-gray-400" />
      </template>
    </BaseEmptyState>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="srv in clinicServicesStore.services"
        :key="srv.id"
        class="card card-hover !p-0 overflow-hidden flex flex-col"
      >
        <div class="h-44 w-full bg-gray-100 overflow-hidden relative">
          <img :src="srv.image_url || '/images/public-service-fallback.svg'" :alt="srv.name" class="h-full w-full object-cover" @error="($event.target as HTMLImageElement).src = '/images/public-service-fallback.svg'" />
        </div>

        <div class="p-6 flex-1 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <span v-if="srv.specialty" class="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-teal-50 text-teal-700 border border-teal-200">
              {{ srv.specialty.name }}
            </span>
          </div>

          <h3 class="text-xl font-bold text-gray-900 mb-2">{{ srv.name }}</h3>

          <p v-if="srv.description" class="text-sm text-gray-600 leading-relaxed mb-4 flex-1">
            {{ srv.description }}
          </p>
          <p v-else class="text-sm text-gray-400 italic mb-4 flex-1">
            No detailed description available for this service.
          </p>

          <div class="pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <span class="inline-flex items-center gap-1 text-green-700 font-medium bg-green-50 px-2 py-0.5 rounded">
              <LucideCheck class="h-3.5 w-3.5" />
              Available Service
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
