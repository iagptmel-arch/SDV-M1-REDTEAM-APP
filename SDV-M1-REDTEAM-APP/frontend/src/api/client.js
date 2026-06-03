/**
 * Client API pour la communication avec le backend FastAPI
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request(endpoint, options = {}, extraHeaders = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...extraHeaders,
      ...options.headers,
    },
    ...options,
  }

  const response = await fetch(url, config)
  if (!response.ok) {
    let detail = `Erreur ${response.status}: ${response.statusText}`
    try {
      const errBody = await response.json()
      if (errBody.detail) detail = errBody.detail
    } catch {
      // ignore parse error
    }
    throw new Error(detail)
  }
  return response.json()
}

function buildQueryString(params = {}) {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
  if (!entries.length) return ''
  return '?' + new URLSearchParams(entries).toString()
}

export default {
  // Hosts
  getHosts: (params = {}, extraHeaders = {}) =>
    request(`/api/v1/hosts${buildQueryString(params)}`, {}, extraHeaders),

  getHost: (id, extraHeaders = {}) =>
    request(`/api/v1/hosts/${id}`, {}, extraHeaders),

  // Services
  getServices: (params = {}, extraHeaders = {}) =>
    request(`/api/v1/services${buildQueryString(params)}`, {}, extraHeaders),

  getService: (id, extraHeaders = {}) =>
    request(`/api/v1/services/${id}`, {}, extraHeaders),

  // Vulnerabilities
  getVulnerabilities: (params = {}, extraHeaders = {}) =>
    request(`/api/v1/vulnerabilities${buildQueryString(params)}`, {}, extraHeaders),

  getVulnerability: (id, extraHeaders = {}) =>
    request(`/api/v1/vulnerabilities/${id}`, {}, extraHeaders),

  // Dashboard
  getDashboardStats: (extraHeaders = {}) =>
    request('/api/v1/dashboard/stats', {}, extraHeaders),

  // Campaigns
  getCampaigns: (params = {}, extraHeaders = {}) =>
    request(`/api/v1/campaigns${buildQueryString(params)}`, {}, extraHeaders),

  getCampaign: (id, extraHeaders = {}) =>
    request(`/api/v1/campaigns/${id}`, {}, extraHeaders),

  createCampaign: (data, extraHeaders = {}) =>
    request('/api/v1/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    }, extraHeaders),

  // Auth
  login: (credentials) =>
    request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
}
