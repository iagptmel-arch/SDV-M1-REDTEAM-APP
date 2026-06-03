<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase"
    :class="badgeClass"
  >
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  severity: {
    type: String,
    default: 'info',
  },
})

const config = {
  critical: { bg: 'bg-red-600 text-white', label: 'Critique' },
  high:     { bg: 'bg-orange-500 text-white', label: 'Élevé' },
  medium:   { bg: 'bg-yellow-500 text-white', label: 'Moyen' },
  low:      { bg: 'bg-green-600 text-white', label: 'Faible' },
  info:     { bg: 'bg-blue-600 text-white', label: 'Info' },
}

const resolved = computed(() => config[props.severity] || config.info)
const badgeClass = computed(() => resolved.value.bg)
const label = computed(() => resolved.value.label)
</script>
