import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import App from './App.vue'
import routes, { setupAuthGuard } from './router/index.js'
import './assets/style.css'

// Enregistrer tous les composants Chart.js globalement
Chart.register(...registerables)

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Activer la garde d'authentification
setupAuthGuard(router)

createApp(App).use(router).mount('#app')
