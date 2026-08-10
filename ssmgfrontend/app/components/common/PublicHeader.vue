<script setup lang="ts">
import { ref, watch } from 'vue'

const route = useRoute()
const menuOpen = ref(false)
const isHome = computed(() => route.path === '/')

const navigation = [
  { label: 'Home', to: '/' },
  { label: 'Doctors', to: '/doctors' },
  { label: 'Services', to: '/services' },
  { label: 'Specialties', to: '/specialties' },
]

watch(() => route.path, () => {
  menuOpen.value = false
})
</script>

<template>
  <header
    class="z-50 w-full"
    :class="isHome ? 'absolute inset-x-0 top-0 border-b border-white/20 bg-slate-950/25 text-white backdrop-blur-sm' : 'sticky top-0 border-b border-gray-200 bg-white text-gray-900 shadow-sm'"
  >
    <div class="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <NuxtLink to="/" class="flex items-center gap-2.5 rounded-lg font-bold tracking-tight focus-visible:ring-offset-4" aria-label="SSMG Healthcare home">
        <img src="/images/ssmg-logo.webp" alt="" width="40" height="40" class="h-10 w-10 rounded-full object-cover shadow-sm ring-1 ring-white/30" />
        <span class="text-lg sm:text-xl">SSMG <span class="font-medium">Healthcare</span></span>
      </NuxtLink>

      <nav class="hidden items-center gap-7 lg:flex" aria-label="Public navigation">
        <NuxtLink
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="rounded text-sm font-medium transition-colors"
          :class="isHome ? 'text-white/90 hover:text-white' : 'text-gray-600 hover:text-primary-700'"
        >
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="hidden items-center gap-3 lg:flex">
        <NuxtLink to="/login" class="rounded-lg px-4 py-2.5 text-sm font-semibold" :class="isHome ? 'text-white hover:bg-white/10' : 'text-gray-700 hover:bg-gray-100'">
          Sign In
        </NuxtLink>
        <NuxtLink to="/register" class="btn btn-primary px-5 py-2.5">Create Account</NuxtLink>
      </div>

      <button
        type="button"
        class="inline-flex h-11 w-11 items-center justify-center rounded-lg lg:hidden"
        :class="isHome ? 'text-white hover:bg-white/10' : 'text-gray-700 hover:bg-gray-100'"
        :aria-expanded="menuOpen"
        aria-controls="public-mobile-menu"
        :aria-label="menuOpen ? 'Close navigation menu' : 'Open navigation menu'"
        @click="menuOpen = !menuOpen"
      >
        <LucideX v-if="menuOpen" class="h-6 w-6" aria-hidden="true" />
        <LucideMenu v-else class="h-6 w-6" aria-hidden="true" />
      </button>
    </div>

    <div v-if="menuOpen" id="public-mobile-menu" class="border-t border-gray-200 bg-white px-4 py-5 text-gray-900 shadow-xl lg:hidden">
      <nav class="mx-auto flex max-w-7xl flex-col gap-1" aria-label="Mobile public navigation">
        <NuxtLink v-for="item in navigation" :key="item.to" :to="item.to" class="rounded-lg px-4 py-3 text-base font-medium text-gray-700 hover:bg-primary-50 hover:text-primary-700">
          {{ item.label }}
        </NuxtLink>
        <div class="my-3 border-t border-gray-200" />
        <NuxtLink to="/login" class="rounded-lg px-4 py-3 text-base font-medium text-gray-700 hover:bg-gray-50">Sign In</NuxtLink>
        <NuxtLink to="/register" class="btn btn-primary mt-2 min-h-11">Create Account</NuxtLink>
      </nav>
    </div>
  </header>
</template>
