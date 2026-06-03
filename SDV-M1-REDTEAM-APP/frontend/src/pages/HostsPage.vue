<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Inventaire des hôtes</h1>
        <p class="text-sm text-gray-500 mt-1">Liste des équipements découverts sur le réseau</p>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <!-- Filtre statut -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in statusOptions"
          :key="opt.value"
          class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
          :class="statusFilter === opt.value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'"
          @click="statusFilter = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>

      <DataTable
        :columns="columns"
        :data="hosts"
        :per-page="20"
        :search-keys="['ip', 'hostname', 'os']"
        @row-click="goToHost"
      >
        <template #cell-status="{ row }">
          <StatusBadge :status="row.status" />
        </template>
        <template #cell-ports="{ row }">
          <span class="text-gray-600">{{ row.ports ?? row.port_count ?? '—' }}</span>
        </template>
        <template #actions="{ row }">
          <router-link
            :to="`/hosts/${row.id}`"
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Détails
          </router-link>
        </template>
        <template #empty>
          <EmptyState title="Aucun hôte trouvé" message="Aucun équipement ne correspond à votre recherche" />
        </template>
      </DataTable>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi.js'
import DataTable from '../components/common/DataTable.vue'
import StatusBadge from '../components/common/StatusBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const router = useRouter()
const { getHosts, loading } = useApi()

const hosts = ref([])
const error = ref(null)
const statusFilter = ref('all')

const columns = [
  { key: 'ip', label: 'Adresse IP' },
  { key: 'hostname', label: 'Hostname' },
  { key: 'os', label: 'Système' },
  { key: 'status', label: 'Statut' },
  { key: 'ports', label: 'Ports' },
]

const statusOptions = [
  { value: 'all', label: 'Tous' },
  { value: 'up', label: 'En ligne' },
  { value: 'down', label: 'Hors ligne' },
  { value: 'unknown', label: 'Inconnu' },
]

const filteredHosts = computed(() => {
  if (statusFilter.value === 'all') return hosts.value
  return hosts.value.filter((h) => h.status === statusFilter.value)
})

function goToHost(host) {
  router.push(`/hosts/${host.id}`)
}

onMounted(async () => {
  try {
    const data = await getHosts()
    hosts.value = data.hosts || data
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des hôtes'
  }
})
</script>
