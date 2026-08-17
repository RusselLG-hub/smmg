<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { CalendarCheck, ClipboardCheck, MailCheck, Stethoscope } from '@lucide/vue'
import { useAuthStore } from '~/stores/auth'
import { useDoctorsStore } from '~/stores/doctors'
import { useClinicServicesStore } from '~/stores/clinicServices'

const authStore = useAuthStore()
const doctorsStore = useDoctorsStore()
const servicesStore = useClinicServicesStore()
const router = useRouter()

useSeoMeta({
  title: 'SSMG Healthcare | Find Doctors and Book Appointments',
  description: 'Discover doctors, explore clinic services, check schedules, and manage healthcare appointments online with SSMG.',
})

const featuredDoctors = computed(() => doctorsStore.doctors.slice(0, 3))
const featuredServices = computed(() => servicesStore.services.slice(0, 4))
const assistantRoute = computed(() => authStore.isAuthenticated ? '/ai-assistant' : '/login?redirect=/ai-assistant')

const benefits = [
  { icon: Stethoscope, title: 'Find the right doctor', text: 'Browse active doctor profiles and specialties in one clear directory.' },
  { icon: CalendarCheck, title: 'Plan around availability', text: 'Review available schedules before choosing an appointment time.' },
  { icon: ClipboardCheck, title: 'Manage appointments online', text: 'Keep track of your scheduled visits and appointment updates.' },
  { icon: MailCheck, title: 'Stay informed', text: 'Receive account and transactional appointment updates by email.' },
]

const steps = [
  ['Create your account', 'Register a patient account to access appointment tools.'],
  ['Find a doctor or service', 'Explore the public directory and clinic service catalog.'],
  ['Choose an available time', 'Open a doctor profile and select from available schedules.'],
  ['Manage your appointment', 'Review your upcoming visits from your patient dashboard.'],
]

onMounted(async () => {
  if (!authStore.user) await authStore.fetchUser()

  if (authStore.isAuthenticated && authStore.user) {
    const routes: Record<string, string> = {
      patient: '/patient/dashboard',
      doctor: '/doctor/dashboard',
      staff: '/staff/dashboard',
      admin: '/admin/dashboard',
    }
    const target = routes[authStore.user.role] || '/patient/dashboard'
    await router.replace(target)
    return
  }

  await Promise.all([
    doctorsStore.fetchDoctors(true),
    servicesStore.fetchServices(true),
  ])
})
</script>

<template>
  <div v-if="authStore.isAuthenticated" class="flex min-h-[70vh] items-center justify-center bg-gray-50">
    <div class="text-center">
      <LucideLoader2 class="mx-auto h-10 w-10 animate-spin text-primary-600" />
      <p class="mt-3 text-sm font-medium text-gray-600">Opening your dashboard…</p>
    </div>
  </div>

  <div v-else class="bg-gray-50">
    <section class="hero-photo relative flex min-h-[92svh] items-center overflow-hidden bg-slate-800 pt-20 text-white" aria-labelledby="hero-title">
      <div class="absolute inset-0 bg-gradient-to-r from-slate-950/90 via-slate-900/65 to-slate-900/5" aria-hidden="true" />
      <div class="relative mx-auto w-full max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
        <div class="max-w-2xl">
          <p class="mb-5 inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-2 text-sm font-semibold backdrop-blur-sm">
            <LucideHeartHandshake class="h-4 w-4" aria-hidden="true" /> Care starts with a simpler appointment
          </p>
          <h1 id="hero-title" class="text-4xl font-bold leading-tight tracking-tight sm:text-5xl lg:text-6xl">Healthcare appointments, made simpler.</h1>
          <p class="mt-6 max-w-xl text-lg leading-8 text-slate-100 sm:text-xl">Discover doctors, explore clinic services, view available schedules, and manage your appointments online.</p>
          <div class="mt-9 flex flex-col gap-3 sm:flex-row">
            <NuxtLink to="/doctors" class="btn bg-primary-600 px-6 py-3.5 text-base font-semibold text-white shadow-lg hover:bg-primary-700">
              Find a Doctor <LucideArrowRight class="h-5 w-5" />
            </NuxtLink>
            <NuxtLink to="/services" class="btn border border-white/60 bg-white/10 px-6 py-3.5 text-base font-semibold text-white backdrop-blur-sm hover:bg-white hover:text-gray-900">View Services</NuxtLink>
          </div>
          <p class="mt-5 text-sm text-slate-200">Already have an account? <NuxtLink to="/login" class="font-semibold text-white underline decoration-white/50 underline-offset-4 hover:decoration-white">Sign in to manage appointments</NuxtLink>.</p>
        </div>
      </div>
      <div class="absolute bottom-7 left-1/2 hidden -translate-x-1/2 items-center gap-2 text-xs font-medium text-white/80 sm:flex" aria-hidden="true">
        <LucideChevronDown class="h-4 w-4" /> Explore SSMG
      </div>
    </section>

    <section class="border-b border-gray-200 bg-white py-20 sm:py-24" aria-labelledby="benefits-title">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="max-w-2xl">
          <p class="text-sm font-bold uppercase tracking-widest text-primary-700">Care, organized</p>
          <h2 id="benefits-title" class="mt-3 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">The essentials for planning your clinic visit</h2>
        </div>
        <div class="mt-12 grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-4">
          <article v-for="benefit in benefits" :key="benefit.title">
            <span class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-700"><component :is="benefit.icon" class="h-6 w-6" /></span>
            <h3 class="mt-5 text-lg font-bold text-gray-900">{{ benefit.title }}</h3>
            <p class="mt-2 text-sm leading-6 text-gray-600">{{ benefit.text }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="py-20 sm:py-24" aria-labelledby="steps-title">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <p class="text-sm font-bold uppercase tracking-widest text-teal-700">How it works</p>
          <h2 id="steps-title" class="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl">From search to scheduled visit</h2>
        </div>
        <ol class="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <li v-for="(step, index) in steps" :key="step[0]" class="relative rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <span class="flex h-10 w-10 items-center justify-center rounded-full bg-teal-600 text-sm font-bold text-white">{{ index + 1 }}</span>
            <h3 class="mt-5 font-bold text-gray-900">{{ step[0] }}</h3>
            <p class="mt-2 text-sm leading-6 text-gray-600">{{ step[1] }}</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="border-y border-gray-200 bg-white py-20 sm:py-24" aria-labelledby="services-title">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div class="max-w-2xl"><p class="text-sm font-bold uppercase tracking-widest text-primary-700">Clinic services</p><h2 id="services-title" class="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl">Explore available care</h2><p class="mt-4 text-gray-600">Browse active services provided through the clinic.</p></div>
          <NuxtLink to="/services" class="btn btn-secondary self-start">View all services <LucideArrowRight class="h-4 w-4" /></NuxtLink>
        </div>
        <div v-if="servicesStore.loading" class="mt-10 flex justify-center py-12"><LucideLoader2 class="h-7 w-7 animate-spin text-primary-600" /></div>
        <div v-else-if="featuredServices.length" class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <article v-for="service in featuredServices" :key="service.id" class="rounded-xl border border-gray-200 bg-gray-50 p-6">
            <span class="flex h-11 w-11 items-center justify-center rounded-lg bg-white text-teal-700 shadow-sm"><LucideHeartHandshake class="h-5 w-5" /></span>
            <h3 class="mt-5 font-bold text-gray-900">{{ service.name }}</h3>
            <p v-if="service.specialty" class="mt-1 text-xs font-semibold uppercase tracking-wide text-primary-700">{{ service.specialty.name }}</p>
            <p class="mt-3 line-clamp-3 text-sm leading-6 text-gray-600">{{ service.description || 'View this service in the catalog for more information.' }}</p>
          </article>
        </div>
        <div v-else class="mt-10 rounded-xl border border-dashed border-gray-300 bg-gray-50 px-6 py-10 text-center"><LucideClipboardList class="mx-auto h-8 w-8 text-gray-400" /><p class="mt-3 font-semibold text-gray-900">No active services are listed yet</p><p class="mt-1 text-sm text-gray-600">Please check the service catalog again later.</p></div>
      </div>
    </section>

    <section class="py-20 sm:py-24" aria-labelledby="doctors-title">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div><p class="text-sm font-bold uppercase tracking-widest text-teal-700">Doctor directory</p><h2 id="doctors-title" class="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl">Meet available doctors</h2></div>
          <NuxtLink to="/doctors" class="btn btn-secondary self-start">Browse all doctors <LucideArrowRight class="h-4 w-4" /></NuxtLink>
        </div>
        <div v-if="doctorsStore.loading" class="mt-10 flex justify-center py-12"><LucideLoader2 class="h-7 w-7 animate-spin text-primary-600" /></div>
        <div v-else-if="featuredDoctors.length" class="mt-10 grid gap-6 md:grid-cols-3">
          <article v-for="doctor in featuredDoctors" :key="doctor.id" class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
            <div class="flex items-center gap-4 p-6">
              <div class="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-full border border-primary-100 bg-primary-50">
                <BaseAvatar :src="doctor.profile_image_url" :alt="`Portrait of Dr. ${doctor.user.name}`" />
              </div>
              <div class="min-w-0"><h3 class="font-bold text-gray-900">Dr. {{ doctor.user.name }}</h3><p class="mt-1 text-sm font-medium text-teal-700">{{ doctor.specialty?.name || 'General healthcare' }}</p></div>
            </div>
            <p v-if="doctor.bio" class="mx-6 line-clamp-2 text-sm leading-6 text-gray-600">{{ doctor.bio }}</p>
            <div class="mt-6 border-t border-gray-200 bg-gray-50 px-6 py-4"><NuxtLink :to="`/doctors/${doctor.id}`" class="inline-flex items-center gap-1 text-sm font-semibold text-primary-700 hover:text-primary-800">View doctor <LucideChevronRight class="h-4 w-4" /></NuxtLink></div>
          </article>
        </div>
        <div v-else class="mt-10 rounded-xl border border-dashed border-gray-300 bg-white px-6 py-10 text-center"><LucideUsers class="mx-auto h-8 w-8 text-gray-400" /><p class="mt-3 font-semibold text-gray-900">No active doctors are listed yet</p><p class="mt-1 text-sm text-gray-600">Please check the doctor directory again later.</p></div>
      </div>
    </section>

    <section class="bg-primary-50 py-20 sm:py-24" aria-labelledby="assistant-title">
      <div class="mx-auto grid max-w-7xl items-center gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
        <div class="rounded-2xl border border-primary-100 bg-white p-8 shadow-sm sm:p-10">
          <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-100 text-teal-700"><LucideBot class="h-7 w-7" /></div>
          <div class="mt-8 space-y-4 text-sm text-gray-600"><div class="mr-8 rounded-xl rounded-bl-sm bg-gray-100 p-4">Get general health information and basic first-aid guidance.</div><div class="ml-8 rounded-xl rounded-br-sm bg-primary-600 p-4 text-white">I can share general information, but I cannot diagnose or replace a healthcare professional.</div></div>
        </div>
        <div>
          <p class="text-sm font-bold uppercase tracking-widest text-primary-700">AI Health & First-Aid Assistant</p>
          <h2 id="assistant-title" class="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl">Helpful information, with clear limits</h2>
          <p class="mt-5 text-lg leading-8 text-gray-600">Use the assistant for general health information and basic first-aid guidance. It does not provide a diagnosis and is not a substitute for professional medical care.</p>
          <p class="mt-4 text-sm font-medium text-gray-700">For emergencies, contact the appropriate emergency medical services immediately.</p>
          <NuxtLink :to="assistantRoute" class="btn btn-primary mt-7 px-5 py-3">Open Health Assistant <LucideArrowRight class="h-4 w-4" /></NuxtLink>
        </div>
      </div>
    </section>

    <section class="bg-slate-900 py-16 text-white sm:py-20" aria-labelledby="final-cta-title">
      <div class="mx-auto flex max-w-7xl flex-col items-start justify-between gap-8 px-4 sm:px-6 lg:flex-row lg:items-center lg:px-8">
        <div><h2 id="final-cta-title" class="text-3xl font-bold sm:text-4xl">Ready to plan your next clinic visit?</h2><p class="mt-3 text-lg text-slate-300">Start by finding the doctor or service that fits your needs.</p></div>
        <div class="flex flex-col gap-3 sm:flex-row"><NuxtLink to="/doctors" class="btn bg-primary-600 px-6 py-3 text-white hover:bg-primary-700">Find a Doctor</NuxtLink><NuxtLink to="/register" class="btn border border-white/40 px-6 py-3 text-white hover:bg-white hover:text-gray-900">Create Account</NuxtLink></div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero-photo { background-image: url('/images/healthcare-consultation-hero.jpg'); background-position: 64% center; background-repeat: no-repeat; background-size: cover; }
@media (max-width: 640px) { .hero-photo { background-position: 58% center; } }
</style>
