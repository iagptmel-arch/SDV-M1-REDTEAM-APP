<template>
  <div class="flex flex-col items-center justify-center py-16">
    <div class="w-16 h-16 mb-4 rounded-full bg-gray-100 flex items-center justify-center">
      <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
    </div>
    <h3 class="text-lg font-medium text-gray-600">{{ title }}</h3>
    <p v-if="message" class="mt-1 text-sm text-gray-400">{{ message }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Aucune donnée' },
  message: { type: String, default: '' },
})
</script>
