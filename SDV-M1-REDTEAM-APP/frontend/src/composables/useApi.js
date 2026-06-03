/**
 * Composable API — wrapper Vue 3 autour du client HTTP
 * Gère le token JWT, le loading state et les erreurs
 */
import { ref } from 'vue'
import client from '../api/client.js'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  function getToken() {
    return localStorage.getItem('access_token')
  }

  function authHeaders() {
    const token = getToken()
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  async function request(method, ...args) {
    loading.value = true
    error.value = null
    try {
      const fn = client[method]
      if (!fn) throw new Error(`Méthode API inconnue: ${method}`)
      const result = await fn(...args, authHeaders())
      return result
    } catch (err) {
      error.value = err.message || 'Erreur API'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Wrappers par endpoint
  async function login(credentials) {
    const data = await request('login', credentials)
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    return data
  }

  async function getDashboardStats() {
    return request('getDashboardStats')
  }

  async function getHosts(params = {}) {
    return request('getHosts', params)
  }

  async function getHost(id) {
    return request('getHost', id)
  }

  async function getServices(params = {}) {
    return request('getServices', params)
  }

  async function getService(id) {
    return request('getService', id)
  }

  async function getVulnerabilities(params = {}) {
    return request('getVulnerabilities', params)
  }

  async function getVulnerability(id) {
    return request('getVulnerability', id)
  }

  async function getCampaigns(params = {}) {
    return request('getCampaigns', params)
  }

  async function getCampaign(id) {
    return request('getCampaign', id)
  }

  async function createCampaign(data) {
    return request('createCampaign', data)
  }

  return {
    loading,
    error,
    login,
    getDashboardStats,
    getHosts,
    getHost,
    getServices,
    getService,
    getVulnerabilities,
    getVulnerability,
    getCampaigns,
    getCampaign,
    createCampaign,
  }
}
