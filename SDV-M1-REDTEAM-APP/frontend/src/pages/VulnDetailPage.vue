<template>
  <div class="space-y-6">
    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else-if="vuln">
      <!-- Retour -->
      <router-link to="/vulnerabilities" class="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline mb-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour aux vulnérabilités
      </router-link>

      <!-- Carte principale -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-800 font-mono">{{ vuln.cve || vuln.id }}</h1>
            <p class="text-gray-500 mt-1">{{ vuln.name || vuln.description?.slice(0, 100) }}</p>
          </div>
          <SeverityBadge :severity="vuln.severity" />
        </div>

        <!-- Score CVSS -->
        <div class="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Score CVSS</p>
            <p class="text-2xl font-bold mt-1" :class="cvssColorClass">
              {{ vuln.cvss ?? 'N/A' }}
            </p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Service associé</p>
            <p class="text-sm font-medium text-gray-700 mt-1">{{ vuln.service_name || vuln.service?.name || '—' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Techniques MITRE</p>
            <p class="text-sm font-medium text-gray-700 mt-1">{{ mitreTechniques.length }} technique(s)</p>
          </div>
        </div>

        <!-- Barre CVSS -->
        <div v-if="vuln.cvss" class="mt-4">
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div
              class="h-2.5 rounded-full transition-all"
              :class="cvssBarClass"
              :style="{ width: cvssPercent + '%' }"
            />
          </div>
        </div>

        <!-- Description -->
        <div v-if="vuln.description" class="mt-6">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Description</h3>
          <p class="text-sm text-gray-600 leading-relaxed">{{ vuln.description }}</p>
        </div>
      </div>

      <!-- Techniques MITRE ATT&CK -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-base font-semibold text-gray-700 mb-4">Techniques MITRE ATT&CK</h2>

        <div v-if="mitreTechniques.length === 0" class="text-center py-8 text-gray-400 text-sm">
          Aucune technique MITRE associée
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="(tech, idx) in mitreTechniques"
            :key="idx"
            class="flex items-start gap-4 p-4 rounded-lg bg-gray-50"
          >
            <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
              <span class="text-blue-700 text-xs font-bold">{{ tech.tactic?.slice(0, 2) || 'MT' }}</span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-gray-700">{{ tech.name || tech.technique }}</p>
              <p class="text-xs text-gray-400 mt-0.5">
                <span class="font-mono">{{ tech.id || tech.technique_id }}</span>
                <span v-if="tech.tactic" class="ml-2 px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                  {{ tech.tactic }}
                </span>
              </p>
              <p v-if="tech.description" class="text-xs text-gray-500 mt-1">{{ tech.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '../composables/useApi.js'
import SeverityBadge from '../components/common/SeverityBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'

const route = useRoute()
const { getVulnerability, loading } = useApi()

const vuln = ref(null)
const error = ref(null)
const mitreTechniques = ref([])

const cvssColorClass = computed(() => {
  const score = parseFloat(vuln.value?.cvss)
  if (score >= 9) return 'text-red-600'
  if (score >= 7) return 'text-orange-500'
  if (score >= 4) return 'text-yellow-500'
  return 'text-green-600'
})

const cvssBarClass = computed(() => {
  const score = parseFloat(vuln.value?.cvss)
  if (score >= 9) return 'bg-red-600'
  if (score >= 7) return 'bg-orange-500'
  if (score >= 4) return 'bg-yellow-500'
  return 'bg-green-600'
})

const cvssPercent = computed(() => {
  const score = parseFloat(vuln.value?.cvss)
  if (isNaN(score)) return 0
  return (score / 10) * 100
})

async function fetchVuln() {
  error.value = null
  try {
    const data = await getVulnerability(route.params.id)
    vuln.value = data.vulnerability || data
    mitreTechniques.value = data.mitre_techniques || (data.vulnerability?.mitre_techniques) || []
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement'
  }
}

onMounted(fetchVuln)
watch(() => route.params.id, fetchVuln)
</script>
