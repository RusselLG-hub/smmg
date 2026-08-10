<template>
  <footer class="border-t border-gray-200 bg-white">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr]">
        <div class="max-w-sm">
          <NuxtLink to="/" class="inline-flex items-center gap-2.5 rounded-lg text-gray-900" aria-label="SSMG Healthcare home">
            <img src="/images/ssmg-logo.webp" alt="" width="40" height="40" loading="lazy" class="h-10 w-10 rounded-full object-cover shadow-sm ring-1 ring-gray-200" />
            <span class="text-xl font-bold">SSMG Healthcare</span>
          </NuxtLink>
          <p class="mt-4 text-sm leading-6 text-gray-600">A simple way to discover doctors, explore clinic services, and manage healthcare appointments online.</p>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-gray-900">Explore</h2>
          <nav class="mt-4 flex flex-col gap-3 text-sm text-gray-600" aria-label="Footer explore navigation">
            <NuxtLink to="/" class="hover:text-primary-700">Home</NuxtLink>
            <NuxtLink to="/doctors" class="hover:text-primary-700">Doctors</NuxtLink>
            <NuxtLink to="/services" class="hover:text-primary-700">Services</NuxtLink>
            <NuxtLink to="/login" class="hover:text-primary-700">Sign In</NuxtLink>
          </nav>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-gray-900">Information</h2>
          <nav class="mt-4 flex flex-col gap-3 text-sm text-gray-600" aria-label="Footer legal navigation">
            <NuxtLink to="/privacy" class="hover:text-primary-700">Privacy Policy</NuxtLink>
            <NuxtLink to="/terms" class="hover:text-primary-700">Terms of Service</NuxtLink>
          </nav>
        </div>
      </div>
      <div class="mt-10 border-t border-gray-200 pt-6 text-sm text-gray-500">© {{ new Date().getFullYear() }} SSMG Healthcare Appointment System.</div>
    </div>
  </footer>
</template>
