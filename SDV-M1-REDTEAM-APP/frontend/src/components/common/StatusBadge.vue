<template>
  <span
    class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="badgeClass"
  >
    <span class="w-1.5 h-1.5 rounded-full" :class="dotClass" />
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'unknown',
  },
})

const config = {
  up:      { bg: 'bg-green-100 text-green-800', dot: 'bg-green-500', label: 'En ligne' },
  running: { bg: 'bg-green-100 text-green-800', dot: 'bg-green-500', label: 'En cours' },
  down:    { bg: 'bg-red-100 text-red-800',     dot: 'bg-red-500',   label: 'Hors ligne' },
  failed:  { bg: 'bg-red-100 text-red-800',     dot: 'bg-red-500',   label: 'Échec' },
  draft:   { bg: 'bg-gray-100 text-gray-800',   dot: 'bg-gray-400',  label: 'Brouillon' },
  completed: { bg: 'bg-blue-100 text-blue-800', dot: 'bg-blue-500', label: 'Terminé' },
  unknown: { bg: 'bg-gray-100 text-gray-800',   dot: 'bg-gray-400',  label: 'Inconnu' },
}

const resolved = computed(() => config[props.status] || config.unknown)
const badgeClass = computed(() => resolved.value.bg)
const dotClass = computed(() => resolved.value.dot)
const label = computed(() => resolved.value.label)
</script>
