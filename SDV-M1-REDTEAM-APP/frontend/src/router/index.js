/**
 * Configuration des routes
 */

import Dashboard from '../components/Dashboard.vue'
import HostList from '../components/HostList.vue'
import ServiceDetail from '../components/ServiceDetail.vue'
import VulnerabilityView from '../components/VulnerabilityView.vue'
import CampaignManager from '../components/CampaignManager.vue'
import ReportViewer from '../components/ReportViewer.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/hosts', name: 'Hosts', component: HostList },
  { path: '/services', name: 'Services', component: ServiceDetail },
  { path: '/vulnerabilities', name: 'Vulnerabilities', component: VulnerabilityView },
  { path: '/campaigns', name: 'Campaigns', component: CampaignManager },
  { path: '/reports', name: 'Reports', component: ReportViewer },
]

export default routes
