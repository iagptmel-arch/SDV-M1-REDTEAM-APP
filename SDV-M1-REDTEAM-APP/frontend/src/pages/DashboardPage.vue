<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-800">Tableau de bord</h1>
      <p class="text-sm text-gray-500 mt-1">Vue d'ensemble des découvertes et analyses réseau</p>
    </div>

    <!-- Stats -->
    <div v-if="loading" class="flex justify-center py-12">
      <LoadingSpinner />
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <!-- Grille des statistiques -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Hôtes découverts"
          :value="stats.hosts ?? '—'"
          icon="&#x1F5A5;"
          color="#2563eb"
        />
        <StatCard
          title="Services exposés"
          :value="stats.services ?? '—'"
          icon="&#x1F4E1;"
          color="#7c3aed"
        />
        <StatCard
          title="Vulnérabilités"
          :value="stats.vulns ?? '—'"
          icon="&#x26A0;"
          color="#dc2626"
        />
        <StatCard
          title="Campagnes"
          :value="stats.campaigns ?? '—'"
          icon="&#x26A1;"
          color="#ea580c"
        />
      </div>

      <!-- Graphique + Dernières campagnes -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Graphique donut -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-base font-semibold text-gray-700 mb-4">Répartition par sévérité</h2>
          <div class="flex items-center justify-center" style="min-height: 240px;">
            <Doughnut
              v-if="chartData"
              :data="chartData"
              :options="chartOptions"
            />
            <p v-else class="text-gray-400 text-sm">Aucune donnée disponible</p>
          </div>
        </div>

        <!-- Dernières campagnes -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold text-gray-700">Dernières campagnes</h2>
            <router-link to="/campaigns" class="text-sm text-blue-600 hover:underline">Voir tout</router-link>
          </div>
          <div v-if="recentCampaigns.length === 0" class="text-center py-8 text-gray-400 text-sm">
            Aucune campagne pour le moment
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="camp in recentCampaigns"
              :key="camp.id"
              class="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-700 truncate">{{ camp.name }}</p>
                <p class="text-xs text-gray-400">{{ camp.targets || 'Cibles non spécifiées' }}</p>
              </div>
              <div class="flex items-center gap-2">
                <StatusBadge :status="camp.status || 'unknown'" />
                <span class="text-xs text-gray-400">{{ formatDate(camp.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { useApi } from '../composables/useApi.js'
import StatCard from '../components/common/StatCard.vue'
import StatusBadge from '../components/common/StatusBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const { getDashboardStats, getCampaigns } = useApi()
const loading = ref(true)
const error = ref(null)
const stats = ref({})
const recentCampaigns = ref([])

const chartData = ref(null)
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: { font: { size: 12 }, padding: 16 },
    },
  },
  cutout: '65%',
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const [statsData, campaignsData] = await Promise.all([
      getDashboardStats(),
      getCampaigns({ limit: 5 }),
    ])
    stats.value = statsData

    if (campaignsData.campaigns) {
      recentCampaigns.value = campaignsData.campaigns
    } else if (Array.isArray(campaignsData)) {
      recentCampaigns.value = campaignsData
    }

    // Chart data from by_severity
    if (statsData.by_severity) {
      const severity = statsData.by_severity
      const labels = []
      const data = []
      const colors = []
      const severityMap = {
        critical: { label: 'Critique', color: '#dc2626' },
        high: { label: 'Élevé', color: '#ea580c' },
        medium: { label: 'Moyen', color: '#ca8a04' },
        low: { label: 'Faible', color: '#16a34a' },
        info: { label: 'Info', color: '#2563eb' },
      }
      for (const [key, val] of Object.entries(severity)) {
        if (val > 0 && severityMap[key]) {
          labels.push(severityMap[key].label)
          data.push(val)
          colors.push(severityMap[key].color)
        }
      }
      if (data.length) {
        chartData.value = {
          labels,
          datasets: [{ data, backgroundColor: colors, borderWidth: 0 }],
        }
      }
    }
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des données'
  } finally {
    loading.value = false
  }
})
</script>
