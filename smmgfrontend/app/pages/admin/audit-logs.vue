<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import {
  LucideActivity,
  LucideCalendar,
  LucideChevronLeft,
  LucideChevronRight,
  LucideClock,
  LucideEye,
  LucideFileText,
  LucideFilter,
  LucideLaptop,
  LucideRefreshCw,
  LucideSearch,
  LucideShield,
  LucideUser,
  LucideX,
} from 'lucide-vue-next'
import { useAuditLogService, type AuditLogItem } from '~/services/auditLogs'

definePageMeta({ middleware: 'auth' })

const auditService = useAuditLogService()
const logs = ref<AuditLogItem[]>([])
const stats = ref({ total_logs: 0, today_logs: 0, actions_count: {} as Record<string, number> })
const pagination = ref({ current_page: 1, last_page: 1, per_page: 20, total: 0 })
const page = ref(1)
const search = ref('')
const actionFilter = ref('')
const roleFilter = ref('')
const loading = ref(true)
const errorMsg = ref<string | null>(null)
const selectedLog = ref<AuditLogItem | null>(null)

const loadLogs = async (targetPage = page.value) => {
  loading.value = true
  errorMsg.value = null
  try {
    const res = await auditService.getLogs({
      page: targetPage,
      per_page: 20,
      search: search.value.trim() || undefined,
      action: actionFilter.value || undefined,
      role: roleFilter.value || undefined,
    })
    logs.value = res.logs || []
    pagination.value = res.pagination
    stats.value = res.stats
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Failed to load audit logs'
  } finally {
    loading.value = false
  }
}

watch([actionFilter, roleFilter], () => {
  page.value = 1
  loadLogs(1)
})

const handleSearch = () => {
  page.value = 1
  loadLogs(1)
}

const getActionBadgeClass = (action: string) => {
  const act = (action || '').toUpperCase()
  if (act.startsWith('AUTH')) {
    return 'bg-blue-50 text-blue-700 border-blue-200'
  }
  if (act.includes('DELETE') || act.includes('DEACTIVATE') || act.includes('CANCEL')) {
    return 'bg-rose-50 text-rose-700 border-rose-200'
  }
  if (act.includes('CREATE') || act.includes('ADD') || act.includes('CONFIRM')) {
    return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  }
  if (act.includes('UPDATE') || act.includes('STATUS') || act.includes('SCHEDULE')) {
    return 'bg-amber-50 text-amber-700 border-amber-200'
  }
  return 'bg-purple-50 text-purple-700 border-purple-200'
}

const formatDate = (iso: string) => {
  try {
    const d = new Date(iso)
    return {
      date: d.toLocaleDateString(),
      time: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    }
  } catch {
    return { date: iso, time: '' }
  }
}

onMounted(() => {
  loadLogs(1)
})
</script>

<template>
  <div class="space-y-6 p-4 sm:p-6 lg:p-8">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <span class="flex h-11 w-11 items-center justify-center rounded-2xl bg-teal-100 text-teal-700">
          <LucideShield class="h-6 w-6" />
        </span>
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900">Audit Logs</h1>
          <p class="text-sm text-slate-500">
            System-wide audit trail of administrative, authentication, and clinical activity
          </p>
        </div>
      </div>
      <button
        type="button"
        :disabled="loading"
        class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
        @click="loadLogs(page)"
      >
        <LucideRefreshCw class="h-4 w-4" :class="{ 'animate-spin text-teal-600': loading }" />
        Refresh
      </button>
    </div>

    <!-- Error notice -->
    <div v-if="errorMsg" class="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
      {{ errorMsg }}
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Entries</span>
          <LucideActivity class="h-5 w-5 text-teal-600" />
        </div>
        <p class="mt-3 text-3xl font-bold text-slate-900">{{ stats.total_logs }}</p>
        <p class="mt-1 text-xs text-slate-500">Recorded audit events</p>
      </div>

      <div class="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Today's Activity</span>
          <LucideClock class="h-5 w-5 text-emerald-600" />
        </div>
        <p class="mt-3 text-3xl font-bold text-slate-900">{{ stats.today_logs }}</p>
        <p class="mt-1 text-xs text-slate-500">Logged since 00:00 UTC</p>
      </div>

      <div class="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Showing</span>
          <LucideFileText class="h-5 w-5 text-blue-600" />
        </div>
        <p class="mt-3 text-3xl font-bold text-slate-900">{{ logs.length }}</p>
        <p class="mt-1 text-xs text-slate-500">Entries on current page</p>
      </div>
    </div>

    <!-- Filter toolbar -->
    <div class="rounded-2xl border border-blue-100 bg-white p-4 shadow-sm">
      <form class="flex flex-col gap-3 md:flex-row md:items-center" @submit.prevent="handleSearch">
        <div class="relative flex-1">
          <LucideSearch class="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Search descriptions, actions, users, IPs..."
            class="w-full rounded-xl border border-slate-200 py-2 pl-10 pr-4 text-sm text-slate-900 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
          />
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <div class="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5">
            <LucideFilter class="h-3.5 w-3.5 text-slate-500" />
            <select
              v-model="actionFilter"
              class="bg-transparent text-xs font-medium text-slate-700 focus:outline-none"
            >
              <option value="">All Actions</option>
              <option value="AUTH_LOGIN">AUTH_LOGIN</option>
              <option value="USER_CREATE_STAFF">USER_CREATE_STAFF</option>
              <option value="USER_STATUS_CHANGE">USER_STATUS_CHANGE</option>
            </select>
          </div>

          <div class="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5">
            <LucideUser class="h-3.5 w-3.5 text-slate-500" />
            <select
              v-model="roleFilter"
              class="bg-transparent text-xs font-medium text-slate-700 focus:outline-none"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="doctor">Doctor</option>
              <option value="staff">Staff</option>
              <option value="patient">Patient</option>
              <option value="system">System</option>
            </select>
          </div>

          <button
            type="submit"
            class="rounded-xl bg-teal-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-teal-700"
          >
            Filter
          </button>
        </div>
      </form>
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-2xl border border-blue-100 bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500">
            <tr>
              <th scope="col" class="px-6 py-4">Timestamp</th>
              <th scope="col" class="px-6 py-4">Actor</th>
              <th scope="col" class="px-6 py-4">Action</th>
              <th scope="col" class="px-6 py-4">Description</th>
              <th scope="col" class="px-6 py-4">IP Address</th>
              <th scope="col" class="px-6 py-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading">
              <td colspan="6" class="py-12 text-center text-slate-500">
                <LucideRefreshCw class="mx-auto h-6 w-6 animate-spin text-teal-600" />
                <p class="mt-2 text-sm">Loading audit logs...</p>
              </td>
            </tr>
            <tr v-else-if="logs.length === 0">
              <td colspan="6" class="py-12 text-center text-slate-500">
                <LucideShield class="mx-auto h-8 w-8 text-slate-300" />
                <p class="mt-2 text-sm font-medium text-slate-700">No audit logs found</p>
                <p class="text-xs text-slate-400">Try adjusting your filter or search query</p>
              </td>
            </tr>
            <tr v-for="log in logs" :key="log.id" class="transition-colors hover:bg-slate-50/75">
              <td class="whitespace-nowrap px-6 py-4 text-xs text-slate-500">
                <div class="flex items-center gap-1.5 font-medium text-slate-900">
                  <LucideCalendar class="h-3.5 w-3.5 text-slate-400" />
                  {{ formatDate(log.created_at).date }}
                </div>
                <div class="text-[11px] text-slate-400">
                  {{ formatDate(log.created_at).time }}
                </div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="font-semibold text-slate-900">{{ log.user_name || 'System' }}</div>
                <span class="inline-flex items-center rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
                  {{ log.user_role || 'System' }}
                </span>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <span
                  class="inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-semibold"
                  :class="getActionBadgeClass(log.action)"
                >
                  {{ log.action }}
                </span>
              </td>
              <td class="max-w-md px-6 py-4">
                <p class="truncate font-medium text-slate-800" :title="log.description">
                  {{ log.description }}
                </p>
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-xs font-mono text-slate-500">
                {{ log.ip_address || '-' }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right">
                <button
                  type="button"
                  class="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
                  @click="selectedLog = log"
                >
                  <LucideEye class="h-3.5 w-3.5" />
                  Inspect
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.last_page > 1" class="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-3">
        <span class="text-xs text-slate-500">
          Page <span class="font-semibold text-slate-900">{{ pagination.current_page }}</span> of
          <span class="font-semibold text-slate-900">{{ pagination.last_page }}</span> ({{ pagination.total }} entries)
        </span>
        <div class="flex items-center gap-2">
          <button
            type="button"
            :disabled="pagination.current_page <= 1"
            class="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm disabled:opacity-40 hover:bg-slate-50"
            @click="page = Math.max(1, page - 1); loadLogs(page)"
          >
            <LucideChevronLeft class="h-3.5 w-3.5" /> Previous
          </button>
          <button
            type="button"
            :disabled="pagination.current_page >= pagination.last_page"
            class="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm disabled:opacity-40 hover:bg-slate-50"
            @click="page = Math.min(pagination.last_page, page + 1); loadLogs(page)"
          >
            Next <LucideChevronRight class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Inspect Modal -->
    <div
      v-if="selectedLog"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs"
    >
      <div class="relative w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl">
        <div class="flex items-start justify-between border-b border-slate-100 pb-4">
          <div class="flex items-center gap-3">
            <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100 text-teal-700">
              <LucideShield class="h-5 w-5" />
            </span>
            <div>
              <h3 class="text-lg font-bold text-slate-900">Audit Entry {{ selectedLog.id }}</h3>
              <p class="text-xs text-slate-500">
                {{ formatDate(selectedLog.created_at).date }} {{ formatDate(selectedLog.created_at).time }}
              </p>
            </div>
          </div>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            @click="selectedLog = null"
          >
            <LucideX class="h-5 w-5" />
          </button>
        </div>

        <div class="mt-4 space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div class="grid grid-cols-2 gap-4 text-xs">
            <div class="rounded-xl border border-slate-100 bg-slate-50 p-3">
              <span class="font-semibold text-slate-500 uppercase">Actor</span>
              <p class="mt-1 font-bold text-slate-900">{{ selectedLog.user_name || 'System' }}</p>
              <p class="text-slate-500">{{ selectedLog.user_role || 'System' }}</p>
            </div>
            <div class="rounded-xl border border-slate-100 bg-slate-50 p-3">
              <span class="font-semibold text-slate-500 uppercase">Action</span>
              <p class="mt-1">
                <span
                  class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-bold"
                  :class="getActionBadgeClass(selectedLog.action)"
                >
                  {{ selectedLog.action }}
                </span>
              </p>
            </div>
          </div>

          <div>
            <label class="text-xs font-semibold uppercase text-slate-500">Description</label>
            <p class="mt-1 rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm text-slate-800">
              {{ selectedLog.description }}
            </p>
          </div>

          <div v-if="selectedLog.auditable_type">
            <label class="text-xs font-semibold uppercase text-slate-500">Target Resource</label>
            <div class="mt-1 rounded-xl border border-slate-100 bg-slate-50 p-3 text-xs font-mono text-slate-700">
              {{ selectedLog.auditable_type }} #{{ selectedLog.auditable_id }}
            </div>
          </div>

          <div v-if="selectedLog.properties && Object.keys(selectedLog.properties).length > 0">
            <label class="text-xs font-semibold uppercase text-slate-500">Metadata / Properties</label>
            <pre class="mt-1 overflow-x-auto rounded-xl border border-slate-200 bg-slate-900 p-3 text-xs text-teal-400">
{{ JSON.stringify(selectedLog.properties, null, 2) }}
            </pre>
          </div>

          <div class="border-t border-slate-100 pt-3 text-xs text-slate-500 space-y-1">
            <div class="flex items-center gap-1.5">
              <LucideLaptop class="h-3.5 w-3.5" />
              <span>IP: <code class="font-mono text-slate-800">{{ selectedLog.ip_address }}</code></span>
            </div>
            <div class="truncate" :title="selectedLog.user_agent || ''">
              Agent: <code class="font-mono text-slate-700">{{ selectedLog.user_agent }}</code>
            </div>
          </div>
        </div>

        <div class="mt-5 border-t border-slate-100 pt-4 text-right">
          <button
            type="button"
            class="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-200"
            @click="selectedLog = null"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
