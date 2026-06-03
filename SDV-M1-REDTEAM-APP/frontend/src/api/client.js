/**
 * Client API pour la communication avec le backend FastAPI
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  const response = await fetch(url, config)
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  return response.json()
}

export default {
  // Hosts
  getHosts: () => request('/api/v1/hosts'),
  getHost: (id) => request(`/api/v1/hosts/${id}`),

  // Services
  getServices: () => request('/api/v1/services'),
  getService: (id) => request(`/api/v1/services/${id}`),

  // Vulnerabilities
  getVulnerabilities: () => request('/api/v1/vulnerabilities'),
  getVulnerability: (id) => request(`/api/v1/vulnerabilities/${id}`),

  // Campaigns
  getCampaigns: () => request('/api/v1/campaigns'),
  getCampaign: (id) => request(`/api/v1/campaigns/${id}`),

  // Auth
  login: (credentials) => request('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),
}
