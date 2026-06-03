<template>
  <div class="space-y-6">
    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else-if="host">
      <!-- Bouton retour -->
      <router-link to="/hosts" class="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline mb-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Retour aux hôtes
      </router-link>

      <!-- En-tête -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-start justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-800">{{ host.hostname || host.ip }}</h1>
            <p class="text-gray-500 mt-1 font-mono">{{ host.ip }}</p>
          </div>
          <StatusBadge :status="host.status" />
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Hostname</p>
            <p class="text-sm font-medium text-gray-700 mt-1">{{ host.hostname || '—' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Système d'exploitation</p>
            <p class="text-sm font-medium text-gray-700 mt-1">{{ host.os || '—' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Statut</p>
            <p class="text-sm font-medium text-gray-700 mt-1 capitalize">{{ host.status || '—' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wider">Ports ouverts</p>
            <p class="text-sm font-medium text-gray-700 mt-1">{{ host.port_count ?? (host.services?.length ?? 0) }}</p>
          </div>
        </div>
      </div>

      <!-- Services associés -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-base font-semibold text-gray-700 mb-4">Services détectés</h2>
        <div v-if="!host.services || host.services.length === 0" class="text-center py-8 text-gray-400 text-sm">
          Aucun service détecté sur cet hôte
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Port</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Protocole</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Service</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Version</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Banner</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="(svc, idx) in host.services" :key="idx" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm font-mono text-gray-700">{{ svc.port || '—' }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ svc.protocol || 'tcp' }}</td>
                <td class="px-4 py-3 text-sm text-gray-700">{{ svc.service || svc.name || '—' }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ svc.version || '—' }}</td>
                <td class="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">{{ svc.banner || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '../composables/useApi.js'
import StatusBadge from '../components/common/StatusBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'

const route = useRoute()
const { getHost, loading } = useApi()

const host = ref(null)
const error = ref(null)

async function fetchHost() {
  error.value = null
  try {
    const data = await getHost(route.params.id)
    host.value = data.host || data
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement'
  }
}

onMounted(fetchHost)
watch(() => route.params.id, fetchHost)
</script>
