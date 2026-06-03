<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-800">Services exposés</h1>
      <p class="text-sm text-gray-500 mt-1">Ports et services détectés sur le réseau</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <!-- Filtres -->
      <div class="flex flex-wrap gap-4">
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">Protocole:</label>
          <select
            v-model="filters.protocol"
            class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">Tous</option>
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">Port min:</label>
          <input
            v-model.number="filters.portMin"
            type="number"
            min="1"
            max="65535"
            placeholder="1"
            class="w-20 px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">Port max:</label>
          <input
            v-model.number="filters.portMax"
            type="number"
            min="1"
            max="65535"
            placeholder="65535"
            class="w-20 px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>
      </div>

      <DataTable
        :columns="columns"
        :data="filteredServices"
        :per-page="20"
        :search-keys="['port', 'service', 'name', 'version', 'host_ip']"
      >
        <template #cell-port="{ row }">
          <span class="font-mono font-medium text-gray-700">{{ row.port }}</span>
        </template>
        <template #cell-service="{ row }">
          <span class="font-medium">{{ row.service || row.name || '—' }}</span>
        </template>
        <template #cell-host_ip="{ row }">
          <router-link
            v-if="row.host_id"
            :to="`/hosts/${row.host_id}`"
            class="text-blue-600 hover:underline font-mono text-sm"
          >
            {{ row.host_ip || row.ip || '—' }}
          </router-link>
          <span v-else class="text-gray-500">—</span>
        </template>
        <template #empty>
          <EmptyState title="Aucun service trouvé" message="Aucun service ne correspond à votre recherche" />
        </template>
      </DataTable>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi.js'
import DataTable from '../components/common/DataTable.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const { getServices, loading } = useApi()

const services = ref([])
const error = ref(null)
const filters = ref({
  protocol: '',
  portMin: null,
  portMax: null,
})

const columns = [
  { key: 'port', label: 'Port' },
  { key: 'protocol', label: 'Protocole' },
  { key: 'service', label: 'Service' },
  { key: 'version', label: 'Version' },
  { key: 'banner', label: 'Banner' },
  { key: 'host_ip', label: 'Hôte' },
]

const filteredServices = computed(() => {
  return services.value.filter((s) => {
    if (filters.value.protocol && s.protocol !== filters.value.protocol) return false
    if (filters.value.portMin && (s.port ?? 0) < filters.value.portMin) return false
    if (filters.value.portMax && (s.port ?? 0) > filters.value.portMax) return false
    return true
  })
})

onMounted(async () => {
  try {
    const data = await getServices()
    services.value = data.services || data
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des services'
  }
})
</script>
