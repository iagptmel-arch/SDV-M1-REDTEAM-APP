/**
 * Configuration des routes
 */

import DashboardPage from '../pages/DashboardPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import HostsPage from '../pages/HostsPage.vue'
import HostDetailPage from '../pages/HostDetailPage.vue'
import ServicesPage from '../pages/ServicesPage.vue'
import VulnerabilitiesPage from '../pages/VulnerabilitiesPage.vue'
import VulnDetailPage from '../pages/VulnDetailPage.vue'
import CampaignsPage from '../pages/CampaignsPage.vue'
import ReportsPage from '../pages/ReportsPage.vue'

const routes = [
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/', name: 'Dashboard', component: DashboardPage },
  { path: '/hosts', name: 'Hosts', component: HostsPage },
  { path: '/hosts/:id', name: 'HostDetail', component: HostDetailPage },
  { path: '/services', name: 'Services', component: ServicesPage },
  { path: '/vulnerabilities', name: 'Vulnerabilities', component: VulnerabilitiesPage },
  { path: '/vulnerabilities/:id', name: 'VulnDetail', component: VulnDetailPage },
  { path: '/campaigns', name: 'Campaigns', component: CampaignsPage },
  { path: '/reports', name: 'Reports', component: ReportsPage },
]

export default routes
