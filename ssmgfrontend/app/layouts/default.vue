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
        class="fixed inset-y-0 left-0 z-50 w-64 bg-white/95 backdrop-blur-xl border-r border-slate-200/80 shadow-sm transform transition-transform duration-300 ease-in-out md:translate-x-0 flex flex-col"
        :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <!-- Sidebar Logo -->
        <div class="h-16 flex items-center px-6 border-b border-gray-200 shrink-0">
          <NuxtLink to="/" class="flex items-center gap-2 text-gray-900 hover:opacity-90 transition-opacity">
            <img src="/images/ssmg-logo.webp" alt="" width="32" height="32" class="h-8 w-8 rounded-full object-cover shadow-sm ring-1 ring-gray-200" />
            <span class="text-lg font-bold tracking-tight">SSMG</span>
          </NuxtLink>
        </div>

        <!-- Sidebar Navigation -->
        <div class="flex-1 overflow-y-auto py-4 px-3 space-y-6">
          <!-- Role specific links -->
          <nav class="space-y-1">
            <NuxtLink
              v-for="link in currentNavLinks"
              :key="link.to"
              :to="link.to"
              class="flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors group"
              :class="isActive(link.to) ? 'bg-primary-50 text-primary-700 font-medium border-l-2 border-primary-600' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-2 border-transparent'"
            >
              <component :is="link.icon" class="h-5 w-5 shrink-0" :class="isActive(link.to) ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'" />
              <span>{{ link.name }}</span>
            </NuxtLink>
          </nav>

          <!-- Public links section -->
          <div>
            <div class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Public</div>
            <nav class="space-y-1">
              <NuxtLink
                v-for="link in publicLinks"
                :key="link.to"
                :to="link.to"
                class="flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors group border-l-2 border-transparent"
                :class="isActive(link.to) ? 'bg-primary-50 text-primary-700 font-medium' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
              >
                <component :is="link.icon" class="h-5 w-5 shrink-0" :class="isActive(link.to) ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'" />
                <span>{{ link.name }}</span>
              </NuxtLink>
            </nav>
          </div>
        </div>

        <!-- Sidebar footer -->
        <div class="p-4 border-t border-gray-200 shrink-0">
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
      <div class="md:ml-64 flex flex-col flex-1 min-w-0">
        <!-- Top Header (Authenticated) -->
        <header class="h-16 bg-white/90 backdrop-blur-xl border-b border-slate-200/80 shadow-sm flex items-center justify-between px-4 sm:px-6 lg:px-8 shrink-0 sticky top-0 z-30">
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
              class="flex min-w-0 items-center gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-gray-50"
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
