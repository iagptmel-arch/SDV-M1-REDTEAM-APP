<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Gestion des campagnes</h1>
        <p class="text-sm text-gray-500 mt-1">Lancement et suivi des campagnes d'analyse</p>
      </div>
      <button
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        @click="showCreateModal = true"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nouvelle campagne
      </button>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-else>
      <!-- Liste campagnes -->
      <div v-if="campaigns.length === 0" class="text-center py-12">
        <EmptyState title="Aucune campagne" message="Créez votre première campagne pour commencer l'analyse">
          <button
            class="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
            @click="showCreateModal = true"
          >
            Créer une campagne
          </button>
        </EmptyState>
      </div>

      <div v-else class="grid gap-4">
        <div
          v-for="camp in campaigns"
          :key="camp.id"
          class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <h3 class="text-base font-semibold text-gray-800 truncate">{{ camp.name }}</h3>
                <StatusBadge :status="camp.status || 'unknown'" />
              </div>
              <p class="text-sm text-gray-500 mt-1">{{ camp.description || 'Aucune description' }}</p>
              <div class="flex items-center gap-4 mt-3 text-xs text-gray-400">
                <span>Cibles: {{ camp.targets || 'Non spécifiées' }}</span>
                <span>Créée le {{ formatDate(camp.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal création -->
    <Modal :model-value="showCreateModal" title="Nouvelle campagne" @close="showCreateModal = false">
      <form @submit.prevent="handleCreate" class="space-y-4">
        <div>
          <label for="camp-name" class="block text-sm font-medium text-gray-700 mb-1">Nom de la campagne</label>
          <input
            id="camp-name"
            v-model="form.name"
            type="text"
            required
            placeholder="Ex: Scan réseau interne"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>
        <div>
          <label for="camp-targets" class="block text-sm font-medium text-gray-700 mb-1">Cibles</label>
          <input
            id="camp-targets"
            v-model="form.targets"
            type="text"
            placeholder="Ex: 192.168.1.0/24"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
          <p class="text-xs text-gray-400 mt-1">Séparées par des virgules</p>
        </div>
        <div>
          <label for="camp-desc" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            id="camp-desc"
            v-model="form.description"
            rows="3"
            placeholder="Description optionnelle"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
          />
        </div>

        <div class="text-sm text-red-600" v-if="createError">{{ createError }}</div>
      </form>
      <template #footer>
        <button
          type="button"
          class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          @click="showCreateModal = false"
        >
          Annuler
        </button>
        <button
          type="button"
          :disabled="creating"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg transition-colors"
          @click="handleCreate"
        >
          {{ creating ? 'Création...' : 'Créer' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi.js'
import StatusBadge from '../components/common/StatusBadge.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'
import Modal from '../components/common/Modal.vue'

const { getCampaigns, createCampaign } = useApi()

const campaigns = ref([])
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')

const form = ref({
  name: '',
  targets: '',
  description: '',
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function handleCreate() {
  if (!form.value.name.trim()) return
  creating.value = true
  createError.value = ''
  try {
    const targetsStr = form.value.targets.trim()
    const payload = {
      name: form.value.name.trim(),
      targets: targetsStr ? targetsStr.split(',').map(t => t.trim()).filter(Boolean) : [],
      description: form.value.description.trim(),
    }
    const newCamp = await createCampaign(payload)
    campaigns.value.unshift(newCamp.campaign || newCamp)
    showCreateModal.value = false
    form.value = { name: '', targets: '', description: '' }
  } catch (err) {
    createError.value = err.message || 'Erreur lors de la création'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    const data = await getCampaigns()
    campaigns.value = data.campaigns || data
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement'
  } finally {
    loading.value = false
  }
})
</script>
