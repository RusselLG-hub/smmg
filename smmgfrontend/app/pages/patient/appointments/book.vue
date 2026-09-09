<script setup lang="ts">
definePageMeta({
  middleware: [
    function (to) {
      return navigateTo({
        path: '/book',
        query: to.query,
      })
    },
  ],
})
</script>

<template>
  <div class="flex items-center justify-center py-24">
    <LucideLoader2 class="h-8 w-8 animate-spin text-primary-600" />
  </div>
</template>
