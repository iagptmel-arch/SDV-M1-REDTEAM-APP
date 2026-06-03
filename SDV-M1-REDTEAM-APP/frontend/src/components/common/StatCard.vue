<template>
  <div
    class="relative overflow-hidden rounded-xl bg-white p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
  >
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-500">{{ title }}</p>
        <p class="mt-1 text-3xl font-bold" :style="{ color: color }">{{ value }}</p>
      </div>
      <div
        class="flex items-center justify-center w-12 h-12 rounded-lg"
        :style="{ backgroundColor: color + '20' }"
      >
        <span class="text-xl" :style="{ color: color }" v-html="icon" />
      </div>
    </div>
    <div v-if="subtitle" class="mt-2 text-xs text-gray-400">{{ subtitle }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: [String, Number], default: '—' },
  icon: { type: String, default: '📊' },
  color: { type: String, default: '#2563eb' },
  subtitle: { type: String, default: '' },
})
</script>
