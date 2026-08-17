<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { usePatientService } from '~/services/patient'
import { useDoctorsService } from '~/services/doctors'
import { useRoute, useRouter } from 'vue-router'
import {
  Award,
  BarChart3,
  Bot,
  Calendar,
  ClipboardList,
  Clock,
  HeartHandshake,
  LayoutDashboard,
  Search,
  Settings,
  Stethoscope,
  User,
} from '@lucide/vue'

const authStore = useAuthStore()
const patientService = usePatientService()
const doctorsService = useDoctorsService()
const router = useRouter()
const route = useRoute()
const profileImageUrl = useState<string | null>('patient-profile-image-url', () => null)

const sidebarOpen = ref(false)

onMounted(async () => {
  if (authStore.user?.role === 'patient') {
    try {
      const profile = await patientService.getMyProfile()
      profileImageUrl.value = profile.profile_image_url || null
    } catch {
      profileImageUrl.value = null
    }
  } else if (authStore.user?.role === 'doctor') {
    try {
      const profile = await doctorsService.getMyProfile()
      profileImageUrl.value = profile.profile_image_url || null
    } catch {
      profileImageUrl.value = null
    }
  } else {
    profileImageUrl.value = authStore.user?.profile_image_url || null
  }
})

// Close mobile sidebar on route change
watch(
  () => route.path,
  () => {
    sidebarOpen.value = false
  }
)

const profileRoute = computed(() => {
  const role = authStore.user?.role
  if (role === 'patient') return '/patient/profile'
  if (role === 'doctor') return '/doctor/profile'
  return '/account/profile'
})

const handleLogout = async () => {
  await authStore.logout()
  profileImageUrl.value = null
  await router.push('/login')
}

// Navigation definitions
const patientLinks = [
  { name: 'Dashboard', to: '/patient/dashboard', icon: LayoutDashboard },
  { name: 'Find Doctors', to: '/doctors', icon: Search },
  { name: 'My Appointments', to: '/patient/appointments', icon: Calendar },
  { name: 'My Profile', to: '/patient/profile', icon: User },
  { name: 'AI Assistant', to: '/ai-assistant', icon: Bot },
]

const doctorLinks = [
  { name: 'Dashboard', to: '/doctor/dashboard', icon: LayoutDashboard },
  { name: 'Consultations', to: '/doctor/appointments', icon: ClipboardList },
  { name: 'My Schedule', to: '/admin/schedules', icon: Clock },
  { name: 'My Analytics', to: '/doctor/reports', icon: BarChart3 },
  { name: 'My Profile', to: '/doctor/profile', icon: User },
  { name: 'AI Assistant', to: '/ai-assistant', icon: Bot },
]

const staffLinks = [
  { name: 'Dashboard', to: '/staff/dashboard', icon: LayoutDashboard },
  { name: 'Appointments', to: '/admin/appointments', icon: Calendar },
  { name: 'Reports', to: '/admin/reports', icon: BarChart3 },
  { name: 'My Profile', to: '/account/profile', icon: User },
]

const adminLinks = [
  { name: 'Dashboard', to: '/admin/dashboard', icon: LayoutDashboard },
  { name: 'Appointments', to: '/admin/appointments', icon: Calendar },
  { name: 'Management', to: '/admin', icon: Settings },
  { name: 'Schedules', to: '/admin/schedules', icon: Clock },
  { name: 'Reports', to: '/admin/reports', icon: BarChart3 },
  { name: 'AI Monitoring', to: '/admin/ai-monitoring', icon: Bot },
  { name: 'My Profile', to: '/account/profile', icon: User },
]

const publicLinks = [
  { name: 'Doctors Directory', to: '/doctors', icon: Stethoscope },
  { name: 'Specialties', to: '/specialties', icon: Award },
  { name: 'Services', to: '/services', icon: HeartHandshake },
]

const currentNavLinks = computed(() => {
  const role = authStore.user?.role
  if (role === 'patient') return patientLinks
  if (role === 'doctor') return doctorLinks
  if (role === 'staff') return staffLinks
  if (role === 'admin') return adminLinks
  return []
})

const isActive = (path: string) => {
  if ((path === '/' || path === '/admin') && route.path !== path) return false
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <div class="app-shell min-h-screen flex flex-col font-sans text-gray-900 antialiased">
    
    <!-- AUTHENTICATED LAYOUT -->
    <template v-if="authStore.isAuthenticated">
      <!-- Mobile sidebar overlay -->
      <Transition
        enter-active-class="transition-opacity ease-linear duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity ease-linear duration-300"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="sidebarOpen" class="fixed inset-0 bg-gray-900/80 z-40 md:hidden" @click="sidebarOpen = false"></div>
      </Transition>

      <!-- Sidebar -->
      <aside
        class="fixed inset-y-0 left-0 z-50 flex w-72 transform flex-col border-r border-slate-200/80 bg-white/95 shadow-xl backdrop-blur-xl transition-transform duration-300 ease-in-out md:translate-x-0"
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <!-- Sidebar Logo -->
        <div class="flex h-20 shrink-0 items-center border-b border-slate-200/80 px-6">
          <NuxtLink to="/" class="flex items-center gap-3 text-slate-950 transition-opacity hover:opacity-90">
            <img src="/images/ssmg-logo.webp" alt="" width="42" height="42" class="h-11 w-11 rounded-2xl object-cover shadow-md ring-1 ring-primary-100" />
            <span><span class="block text-lg font-extrabold tracking-tight">SSMG</span><span class="block text-[10px] font-bold uppercase tracking-[0.18em] text-teal-700">Healthcare</span></span>
          </NuxtLink>
        </div>

        <!-- Sidebar Navigation -->
        <div class="flex-1 space-y-7 overflow-y-auto px-4 py-6">
          <!-- Role specific links -->
          <nav class="space-y-1.5">
            <NuxtLink
              v-for="link in currentNavLinks"
              :key="link.to"
              :to="link.to"
              class="group flex min-h-11 items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm transition-all"
              :class="isActive(link.to) ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold shadow-md shadow-primary-600/20' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'"
            >
              <component :is="link.icon" class="h-5 w-5 shrink-0" :class="isActive(link.to) ? 'text-white' : 'text-slate-400 group-hover:text-primary-600'" />
              <span>{{ link.name }}</span>
            </NuxtLink>
          </nav>

          <!-- Public links section -->
          <div>
            <div class="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Explore healthcare</div>
            <nav class="space-y-1">
              <NuxtLink
                v-for="link in publicLinks"
                :key="link.to"
                :to="link.to"
                class="group flex min-h-10 items-center gap-3 rounded-xl px-3.5 py-2 text-sm transition-colors"
                :class="isActive(link.to) ? 'bg-teal-50 text-teal-800 font-semibold' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'"
              >
                <component :is="link.icon" class="h-5 w-5 shrink-0" :class="isActive(link.to) ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'" />
                <span>{{ link.name }}</span>
              </NuxtLink>
            </nav>
          </div>
        </div>

        <!-- Sidebar footer -->
        <div class="shrink-0 border-t border-slate-200 bg-slate-50/70 p-4">
          <button
            type="button"
            class="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
            @click="handleLogout"
          >
            <LucideLogOut class="h-4 w-4" />
            <span>Log Out</span>
          </button>
        </div>
      </aside>

      <!-- Main Content Area -->
      <div class="flex min-w-0 flex-1 flex-col md:ml-72">
        <!-- Top Header (Authenticated) -->
        <header class="sticky top-0 z-30 flex h-20 shrink-0 items-center justify-between border-b border-white/80 bg-white/85 px-4 shadow-sm backdrop-blur-xl sm:px-6 lg:px-8">
          <div class="flex items-center">
            <!-- Mobile hamburger -->
            <button
              type="button"
              class="md:hidden p-2 -ml-2 mr-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              @click="sidebarOpen = true"
            >
              <LucideMenu class="h-6 w-6" />
            </button>
          </div>
          
          <div class="flex items-center gap-4">
            <FeaturesNotificationsNotificationMenu />
            <NuxtLink v-if="authStore.user?.role === 'patient'" to="/ai-assistant" class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-teal-700 bg-teal-50 hover:bg-teal-100 rounded-md transition-colors border border-teal-200">
              <LucideBot class="h-3.5 w-3.5" />
              <span>AI Health Assistant</span>
            </NuxtLink>
            <NuxtLink
              :to="profileRoute"
              class="flex min-w-0 items-center gap-3 rounded-2xl border border-transparent px-2.5 py-2 transition-all hover:border-slate-200 hover:bg-white hover:shadow-sm"
              aria-label="Open my profile"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary-100 text-sm font-bold text-primary-700 ring-1 ring-gray-200">
                <img
                  v-if="profileImageUrl"
                  :src="profileImageUrl"
                  :alt="`${authStore.user?.name || 'User'} avatar`"
                  class="h-full w-full object-cover"
                />
                <span v-else>{{ authStore.user?.name?.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="hidden min-w-0 text-left sm:block">
                <p class="max-w-40 truncate text-sm font-medium text-gray-900">{{ authStore.user?.name }}</p>
                <p class="max-w-40 truncate text-xs text-gray-500">{{ authStore.user?.email }}</p>
              </div>
            </NuxtLink>
          </div>
        </header>

        <main class="flex-1 p-0">
          <slot />
        </main>
      </div>
    </template>


    <!-- UNAUTHENTICATED / GUEST LAYOUT -->
    <template v-else>
      <CommonPublicHeader />

      <main class="flex-1">
        <slot />
      </main>

      <CommonPublicFooter />
    </template>

  </div>
</template>
