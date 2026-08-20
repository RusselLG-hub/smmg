<script setup lang="ts">
defineProps<{
  eyebrow: string
  title: string
  description: string
  panelTitle: string
  panelDescription: string
}>()
</script>

<template>
  <div class="relative overflow-hidden bg-slate-50 px-4 py-10 sm:px-6 sm:py-14 lg:px-8 lg:py-16">
    <div class="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-primary-100/70 blur-3xl" aria-hidden="true" />
    <div class="pointer-events-none absolute -right-20 bottom-0 h-72 w-72 rounded-full bg-teal-100/60 blur-3xl" aria-hidden="true" />

    <div class="relative mx-auto grid min-h-[680px] max-w-6xl overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-xl shadow-slate-200/60 lg:grid-cols-[1.05fr_0.95fr]">
      <section class="auth-care-panel relative hidden overflow-hidden bg-slate-900 lg:flex lg:flex-col lg:justify-end" aria-label="SMMG Healthcare">
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-900/60 to-slate-900/10" aria-hidden="true" />
        <div class="relative p-10 xl:p-12">
          <div class="mb-7 inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-3.5 py-2 text-sm font-semibold text-white backdrop-blur-sm">
            <img src="/images/smmg-logo.webp" alt="" width="20" height="20" class="h-5 w-5 rounded-full object-cover" />
            SMMG Healthcare
          </div>
          <h2 class="max-w-lg text-3xl font-bold leading-tight tracking-tight text-white xl:text-4xl">{{ panelTitle }}</h2>
          <p class="mt-4 max-w-md text-base leading-7 text-slate-200">{{ panelDescription }}</p>
          <div class="mt-8 grid grid-cols-2 gap-3 text-sm text-white/90">
            <div class="flex items-center gap-2 rounded-xl border border-white/15 bg-white/10 p-3 backdrop-blur-sm"><LucideStethoscope class="h-4 w-4 shrink-0" /> Find doctors</div>
            <div class="flex items-center gap-2 rounded-xl border border-white/15 bg-white/10 p-3 backdrop-blur-sm"><LucideCalendarCheck class="h-4 w-4 shrink-0" /> Plan visits</div>
          </div>
        </div>
      </section>

      <section class="flex items-center px-6 py-10 sm:px-10 lg:px-12 xl:px-16">
        <div class="mx-auto w-full max-w-md">
          <div class="mb-8">
            <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-50 text-primary-700 ring-1 ring-primary-100">
              <slot name="icon" />
            </div>
            <p class="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">{{ eyebrow }}</p>
            <h1 class="mt-2 text-3xl font-bold tracking-tight text-gray-900">{{ title }}</h1>
            <p class="mt-3 text-sm leading-6 text-gray-600">{{ description }}</p>
          </div>

          <slot />

          <div class="mt-8 border-t border-gray-200 pt-6 text-center text-sm text-gray-600">
            <slot name="footer" />
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.auth-care-panel {
  background-image: url('/images/healthcare-consultation-hero.jpg');
  background-position: 61% center;
  background-size: cover;
}
</style>
