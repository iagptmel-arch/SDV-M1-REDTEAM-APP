<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Barre d'outils -->
    <div v-if="showSearch || $slots.toolbar" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 border-b border-gray-100">
      <div v-if="showSearch" class="relative w-full sm:w-72">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher..."
          class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          @input="onSearch"
        />
        <svg class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <div class="flex items-center gap-2 w-full sm:w-auto">
        <slot name="toolbar" />
      </div>
    </div>

    <!-- Tableau -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              :class="col.class || ''"
            >
              {{ col.label }}
            </th>
            <th v-if="$slots.actions" class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-100">
          <tr v-if="filteredData.length === 0">
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="px-4 py-12 text-center">
              <slot name="empty">
                <div class="text-gray-400 text-sm">Aucune donnée</div>
              </slot>
            </td>
          </tr>
          <tr
            v-for="(row, rowIdx) in paginatedData"
            :key="rowIdx"
            class="hover:bg-gray-50 transition-colors"
            :class="{ 'cursor-pointer': $attrs.onRowClick }"
            @click="$emit('rowClick', row)"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 text-sm text-gray-700 whitespace-nowrap"
              :class="col.class || ''"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="getNestedValue(row, col.key)">
                {{ getNestedValue(row, col.key) }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="px-4 py-3 text-right whitespace-nowrap">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50">
      <div class="text-sm text-gray-500">
        {{ (currentPage - 1) * perPage + 1 }}–{{ Math.min(currentPage * perPage, filteredData.length) }} sur {{ filteredData.length }}
      </div>
      <div class="flex items-center gap-1">
        <button
          :disabled="currentPage <= 1"
          class="px-3 py-1 text-sm rounded border border-gray-200 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="prevPage"
        >
          Précédent
        </button>
        <span
          v-for="p in visiblePages"
          :key="p"
          class="px-3 py-1 text-sm rounded cursor-pointer"
          :class="p === currentPage ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 text-gray-600'"
          @click="goToPage(p)"
        >
          {{ p }}
        </span>
        <button
          :disabled="currentPage >= totalPages"
          class="px-3 py-1 text-sm rounded border border-gray-200 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="nextPage"
        >
          Suivant
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  data: { type: Array, default: () => [] },
  perPage: { type: Number, default: 20 },
  showSearch: { type: Boolean, default: true },
  searchKeys: { type: Array, default: () => [] },
})

defineEmits(['rowClick'])

const searchQuery = ref('')
const currentPage = ref(1)

function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, part) => (acc ? acc[part] : undefined), obj)
}

const filteredData = computed(() => {
  if (!searchQuery.value || !props.searchKeys.length) return props.data
  const q = searchQuery.value.toLowerCase()
  return props.data.filter((row) =>
    props.searchKeys.some((key) => {
      const val = getNestedValue(row, key)
      return val && String(val).toLowerCase().includes(q)
    })
  )
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredData.value.length / props.perPage)))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.perPage
  return filteredData.value.slice(start, start + props.perPage)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1)
  if (cur <= 3) return [1, 2, 3, 4, 5]
  if (cur >= total - 2) return [total - 4, total - 3, total - 2, total - 1, total]
  return [cur - 2, cur - 1, cur, cur + 1, cur + 2]
})

function onSearch() {
  currentPage.value = 1
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value--
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++
}

function goToPage(p) {
  currentPage.value = p
}

watch(
  () => props.data,
  () => { currentPage.value = 1 }
)
</script>
