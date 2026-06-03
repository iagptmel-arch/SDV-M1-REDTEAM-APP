<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mb-4">
          <span class="text-2xl font-bold text-white">S</span>
        </div>
        <h1 class="text-2xl font-bold text-white">RedTeam Scanner</h1>
        <p class="text-slate-400 text-sm mt-1">Plateforme de découverte et d'analyse réseau</p>
      </div>

      <!-- Carte -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-6">Connexion</h2>

        <!-- Alerte erreur -->
        <div
          v-if="errorMsg"
          class="mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-center gap-2"
        >
          <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ errorMsg }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Nom d'utilisateur</label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              autocomplete="username"
              placeholder="Votre identifiant"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
              placeholder="Votre mot de passe"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 text-sm text-gray-600">
              <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              Se souvenir de moi
            </label>
            <a href="#" class="text-sm text-blue-600 hover:underline">Mot de passe oublié ?</a>
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg v-if="loading" class="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </form>
      </div>

      <p class="text-center text-slate-500 text-xs mt-6">
        SDV-M1 RedTeam App &mdash; Projet pédagogique
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi.js'

const router = useRouter()
const { login, loading } = useApi()

const username = ref('')
const password = ref('')
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  try {
    await login({ username: username.value, password: password.value })
    router.push('/')
  } catch (err) {
    errorMsg.value = err.message || 'Identifiants invalides'
  }
}
</script>
