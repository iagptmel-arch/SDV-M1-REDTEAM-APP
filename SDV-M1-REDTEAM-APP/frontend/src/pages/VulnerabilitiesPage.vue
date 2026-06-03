<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-800">Vulnérabilités</h1>
      <p class="text-sm text-gray-500 mt-1">Analyse des vulnérabilités et correspondances MITRE ATT&CK</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <!-- Filtres -->
      <div class="flex flex-wrap gap-4">
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">Sévérité:</label>
          <select
            v-model="filters.severity"
            class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">Toutes</option>
            <option value="critical">Critique</option>
            <option value="high">Élevé</option>
            <option value="medium">Moyen</option>
            <option value="low">Faible</option>
            <option value="info">Info</option>
          </select>
        </div>
      </div>

      <DataTable
        :columns="columns"
        :data="filteredVulns"
        :per-page="20"
        :search-keys="['cve_id', 'service_name', 'name']"
        @row-click="goToVuln"
      >
        <template #cell-severity="{ row }">
          <SeverityBadge :severity="row.severity" />
        </template>
        <template #cell-cvss_score="{ row }">
          <span class="font-mono">{{ row.cvss_score ?? '—' }}</span>
        </template>
        <template #cell-mitre="{ row }">
          <span class="text-xs text-gray-500">{{ row.mitre_techniques?.length ?? 0 }} techniques</span>
        </template>
        <template #cell-service_name="{ row }">
          <span class="text-gray-600">{{ row.service_name || '—' }}</span>
        </template>
        <template #actions="{ row }">
          <router-link
            :to="`/vulnerabilities/${row.id}`"
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Détails
          </router-link>
        </template>
        <template #empty>
          <EmptyState title="Aucune vulnérabilité trouvée" message="Aucune vulnérabilité ne correspond à votre recherche" />
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
import SeverityBadge from '../components/common/SeverityBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const router = useRouter()
const { getVulnerabilities, loading } = useApi()

const vulnerabilities = ref([])
const error = ref(null)
const filters = ref({ severity: '' })

const columns = [
  { key: 'cve_id', label: 'CVE' },
  { key: 'service_name', label: 'Service' },
  { key: 'severity', label: 'Sévérité' },
  { key: 'cvss_score', label: 'CVSS' },
  { key: 'mitre', label: 'MITRE' },
]

const filteredVulns = computed(() => {
  if (!filters.value.severity) return vulnerabilities.value
  return vulnerabilities.value.filter((v) => v.severity === filters.value.severity)
})

function goToVuln(vuln) {
  router.push(`/vulnerabilities/${vuln.id}`)
}

onMounted(async () => {
  try {
    const data = await getVulnerabilities()
    vulnerabilities.value = data.vulnerabilities || data
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des vulnérabilités'
  }
})
</script>
