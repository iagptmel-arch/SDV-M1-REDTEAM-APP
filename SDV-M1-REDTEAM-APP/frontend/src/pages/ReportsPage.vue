<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-800">Rapports</h1>
      <p class="text-sm text-gray-500 mt-1">Consultation et export des rapports d'analyse</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <div v-if="reports.length === 0" class="text-center py-12">
        <EmptyState title="Aucun rapport" message="Les rapports apparaîtront ici après l'analyse">
        </EmptyState>
      </div>

      <div v-else class="grid gap-4">
        <div
          v-for="report in reports"
          :key="report.id"
          class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0 flex-1">
              <h3 class="text-base font-semibold text-gray-800">{{ report.name || report.title || 'Rapport' }}</h3>
              <p class="text-sm text-gray-500 mt-1">
                Campagne associée:
                <router-link
                  v-if="report.campaign_id"
                  :to="`/campaigns/${report.campaign_id}`"
                  class="text-blue-600 hover:underline"
                >
                  {{ report.campaign_name || `#${report.campaign_id}` }}
                </router-link>
                <span v-else class="text-gray-400">—</span>
              </p>
              <div class="flex items-center gap-4 mt-2 text-xs text-gray-400">
                <span>Créé le {{ formatDate(report.created_at) }}</span>
                <span>{{ report.type || 'Général' }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                class="px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                @click="exportReport(report, 'pdf')"
              >
                PDF
              </button>
              <button
                class="px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                @click="exportReport(report, 'csv')"
              >
                CSV
              </button>
              <button
                class="px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                @click="exportReport(report, 'json')"
              >
                JSON
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const reports = ref([])
const loading = ref(true)
const error = ref(null)

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

function exportReport(report, format) {
  // Placeholder — à implémenter avec l'API backend
  const filename = `${report.name || 'rapport'}_${report.id}.${format}`
  alert(`Export ${format.toUpperCase()} du rapport "${report.name}" — ${filename}`)
}

onMounted(async () => {
  try {
    // Simuler des données pour l'instant
    // À remplacer par: const data = await getReports()
    // reports.value = data.reports || data
    await new Promise((r) => setTimeout(r, 500))
    reports.value = []
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des rapports'
  } finally {
    loading.value = false
  }
})
</script>
