<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <router-link to="/campaigns" class="text-sm text-blue-600 hover:underline mb-1 inline-block">← Retour aux campagnes</router-link>
        <h1 class="text-2xl font-bold text-gray-800">{{ campaign.name || 'Campagne' }}</h1>
      </div>
      <StatusBadge :status="campaign.status || 'unknown'" size="lg" />
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <!-- Infos campagne -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide">Description</p>
          <p class="text-sm text-gray-700 mt-1">{{ campaign.description || 'Aucune description' }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide">Cibles</p>
          <p class="text-sm text-gray-700 mt-1">{{ formatTargets(campaign.targets) }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide">Dates</p>
          <p class="text-sm text-gray-700 mt-1">
            Créée: {{ formatDate(campaign.created_at) }}<br />
            <span v-if="campaign.started_at">Démarrée: {{ formatDate(campaign.started_at) }}<br /></span>
            <span v-if="campaign.completed_at">Terminée: {{ formatDate(campaign.completed_at) }}</span>
          </p>
        </div>
      </div>

      <!-- Résumé -->
      <div v-if="campaign.summary" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <p class="text-2xl font-bold text-blue-600">{{ campaign.summary.hosts ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Hôtes découverts</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <p class="text-2xl font-bold text-purple-600">{{ campaign.summary.services ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Services trouvés</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
          <p class="text-2xl font-bold text-red-600">{{ campaign.summary.vulnerabilities ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Vulnérabilités</p>
        </div>
      </div>

      <!-- Erreur éventuelle -->
      <div v-if="campaign.error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
        {{ campaign.error }}
      </div>

      <!-- Hôtes découverts -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="text-base font-semibold text-gray-700">Hôtes découverts</h2>
        </div>
        <DataTable
          v-if="hosts.length"
          :columns="hostColumns"
          :data="hosts"
          :per-page="10"
          @row-click="goToHost"
        >
          <template #cell-ip="{ row }">
            <span class="font-mono text-sm">{{ row.ip }}</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge :status="row.status" />
          </template>
        </DataTable>
        <p v-else class="text-center text-gray-400 text-sm py-8">
          {{ campaign.status === 'draft' ? 'Lancez la campagne pour découvrir des hôtes' : 'Aucun hôte découvert' }}
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../composables/useApi.js'
import DataTable from '../components/common/DataTable.vue'
import StatusBadge from '../components/common/StatusBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const { getCampaign, getHosts } = useApi()

const campaign = ref({})
const hosts = ref([])
const loading = ref(true)
const error = ref(null)

const hostColumns = [
  { key: 'ip', label: 'IP' },
  { key: 'hostname', label: 'Hostname' },
  { key: 'mac', label: 'MAC' },
  { key: 'os', label: 'OS' },
  { key: 'status', label: 'Statut' },
]

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatTargets(targets) {
  if (!targets || targets.length === 0) return 'Non spécifiées'
  return targets.join(', ')
}

function goToHost(host) {
  router.push(`/hosts/${host.id}`)
}

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const campId = route.params.id
    const campData = await getCampaign(campId)
    campaign.value = campData.campaign || campData

    // Charger les hôtes de cette campagne
    const hostsData = await getHosts({ campaign_id: campId })
    hosts.value = hostsData.hosts || hostsData
  } catch (err) {
    error.value = err.message || 'Erreur de chargement'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// Recharger quand l'ID change
watch(() => route.params.id, loadData)
</script>
