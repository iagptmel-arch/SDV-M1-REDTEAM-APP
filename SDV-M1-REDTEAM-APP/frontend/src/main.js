import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import App from './App.vue'
import routes from './router/index.js'
import './assets/style.css'

// Enregistrer tous les composants Chart.js globalement
Chart.register(...registerables)

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
