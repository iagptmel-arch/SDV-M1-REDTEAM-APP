<template>
  <div id="app-root" class="min-h-screen bg-slate-100">
    <AppLayout v-if="!isLoginPage">
      <router-view />
    </AppLayout>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from './components/layout/AppLayout.vue'

const route = useRoute()
const isLoginPage = computed(() => route.name === 'Login')
</script>
