# Plan d'architecture UI — SDV-M1-REDTEAM-APP

## Stack technique

| Technologie | Usage |
|-------------|-------|
| Vue 3 (Composition API + `<script setup>`) | Framework |
| Vue Router 4 | Routage SPA |
| Tailwind CSS 3 | Styling responsive |
| Chart.js + vue-chartjs | Graphiques Dashboard |
| fetch (native) | Client API (via `src/api/client.js`) |
| Pinia (future) | State management (optionnel) |

---

## Arborescence des composants

```
App.vue
├── AppLayout.vue                  ← Structure sidebar + topbar + content
│   ├── SidebarNav.vue              ← Navigation latérale
│   ├── TopBar.vue                  ← Barre supérieure (user, search)
│   └── <router-view />            ← Contenu principal
│
├── pages/                         ← Pages (vues)
│   ├── LoginPage.vue              ← Authentification
│   ├── DashboardPage.vue          ← Tableau de bord
│   ├── HostsPage.vue              ← Liste des hôtes
│   ├── HostDetailPage.vue         ← Détail d'un hôte
│   ├── ServicesPage.vue           ← Services / ports
│   ├── ServiceDetailPage.vue      ← Détail d'un service
│   ├── VulnerabilitiesPage.vue    ← Vulnérabilités / CVE
│   ├── VulnDetailPage.vue         ← Détail vulnérabilité + MITRE
│   ├── CampaignsPage.vue          ← Gestion campagnes
│   ├── CampaignDetailPage.vue     ← Détail campagne
│   └── ReportsPage.vue            ← Rapports / exports
│
├── components/                    ← Composants réutilisables
│   ├── common/
│   │   ├── StatusBadge.vue        ← Badge (up/down/critical...)
│   │   ├── SeverityBadge.vue      ← Niveau criticité
│   │   ├── DataTable.vue          ← Tableau avec filtres
│   │   ├── StatCard.vue           ← Carte de statistique
│   │   ├── Modal.vue              ← Fenêtre modale
│   │   ├── LoadingSpinner.vue     ← Indicateur chargement
│   │   ├── EmptyState.vue         ← État vide
│   │   └── ConfirmDialog.vue      ← Dialogue de confirmation
│   │
│   ├── dashboard/
│   │   ├── StatsGrid.vue          ← Grille des stats
│   │   ├── SeverityChart.vue      ← Graphique répartition criticité
│   │   └── RecentScans.vue        ← Derniers scans
│   │
│   ├── hosts/
│   │   ├── HostTable.vue          ← Tableau des hôtes
│   │   └── HostCard.vue           ← Carte hôte (mobile)
│   │
│   ├── services/
│   │   ├── ServiceTable.vue       ← Tableau des services
│   │   └── PortBadge.vue          ← Badge port/protocole
│   │
│   ├── vulnerabilities/
│   │   ├── VulnTable.vue          ← Tableau des vulnérabilités
│   │   ├── CveCard.vue            ← Carte CVE
│   │   └── MitreTechniques.vue    ← Techniques MITRE
│   │
│   └── campaigns/
│       ├── CampaignList.vue       ← Liste campagnes
│       └── CampaignForm.vue       ← Formulaire création
│
├── composables/                   ← Logique réutilisable (Composition API)
│   ├── useApi.js                  ← Wrapper API
│   ├── useAuth.js                 ← Gestion auth (token, user)
│   └── useNotifications.js        ← Notifications toast
│
├── router/
│   └── index.js                   ← Configuration routes
│
├── api/
│   └── client.js                  ← Client HTTP
│
└── assets/
    └── style.css                  ← Tailwind directives
```

---

## Layout principal

```
┌────────────┬──────────────────────────────────────────┐
│            │  TopBar                                   │
│  Sidebar   │  Logo | Search | Notif | User             │
│            ├──────────────────────────────────────────┤
│  ┌──────┐  │                                          │
│  │ Icon │  │  <router-view />                         │
│  │ Dashboard│  Contenu principal de la page            │
│  │      │  │                                          │
│  ├──────┤  │                                          │
│  │ Icon │  │                                          │
│  │ Hosts │  │                                          │
│  │      │  │                                          │
│  ├──────┤  │                                          │
│  │ Icon │  │                                          │
│  │ Services│                                          │
│  │      │  │                                          │
│  ├──────┤  │                                          │
│  │ Icon │  │                                          │
│  │ Vulns │  │                                          │
│  │      │  │                                          │
│  ├──────┤  │                                          │
│  │ Icon │  │                                          │
│  │ Campaigns                                        │
│  │      │  │                                          │
│  ├──────┤  │                                          │
│  │ Icon │  │                                          │
│  │ Reports│                                          │
│  └──────┘  │                                          │
└────────────┴──────────────────────────────────────────┘
```

### Sidebar
- Logo/App name en haut
- Items de navigation avec icônes
- Item actif surligné
- Réductible (hamburger) sur mobile

### TopBar
- Barre de recherche rapide
- Icône notifications + badge
- Avatar utilisateur + dropdown (profil, logout)

---

## Palette de couleurs

```css
/* Primaire */
primary:    #1e40af   (blue-800)
primary-2:  #2563eb   (blue-600)

/* Secondaire */
secondary:  #64748b   (slate-500)

/* Severité */
critical:   #dc2626   (red-600)
high:       #ea580c   (orange-600)
medium:     #ca8a04   (yellow-600)
low:        #16a34a   (green-600)
info:       #2563eb   (blue-600)

/* Layout */
bg-sidebar: #0f172a   (slate-900)
bg-main:    #f1f5f9   (slate-100)
bg-card:    #ffffff
```

---

## Pages détaillées

### 1. Login (`/login`)
- Carte centrée
- Champs : username, password
- Bouton "Se connecter"
- Lien "Mot de passe oublié ?"
- Design clair et sobre

### 2. Dashboard (`/`)
- **StatsGrid** : 4 cartes (Hôtes, Services, Vulnérabilités, Campagnes)
- **SeverityChart** : Graphique donut répartition criticité
- **RecentScans** : Tableau des 5 derniers scans
- **MITRE Overview** : Top techniques MITRE détectées

### 3. Hôtes (`/hosts`)
- **HostTable** : Tableau avec colonnes (IP, Hostname, OS, Status, Ports, Actions)
- Barre de recherche + filtre par statut
- Pagination (20 par page)
- Clic → `/hosts/:id` (détail avec services associés)

### 4. Services (`/services`)
- **ServiceTable** : Colonnes (Port, Protocol, Name, Version, Banner, Host, Actions)
- Filtres par protocole, port range
- Groupement par hôte optionnel

### 5. Vulnérabilités (`/vulnerabilities`)
- **VulnTable** : Colonnes (CVE, Service, Severity, CVSS, MITRE, Action)
- Badge de couleur par sévérité
- Filtres : sévérité, service, date
- Clic → `/vulnerabilities/:id` (détail CVE + techniques MITRE)

### 6. Campagnes (`/campaigns`)
- **CampaignList** : Liste des campagnes (nom, statut, target, date, actions)
- Bouton "Nouvelle campagne"
- **CampaignForm** : Modal de création (nom, targets, description)
- Clic → `/campaigns/:id` (détail avec résultats)

### 7. Rapports (`/reports`)
- Liste des rapports générés
- Boutons d'export (PDF, CSV, JSON)
- Historique des exports
- Lien vers le détail campagne

---

## Timing et priorités (Phase 1)

| Ordre | Page | Priorité | Dépend de |
|-------|------|----------|-----------|
| 1 | AppLayout + Sidebar + TopBar | P0 | — |
| 2 | Dashboard (StatsGrid, statique) | P0 | API stats |
| 3 | HostsPage + HostTable | P0 | API hosts |
| 4 | ServicesPage + ServiceTable | P0 | API services |
| 5 | Dashboard (graphiques) | P1 | API stats |
| 6 | HostDetailPage | P1 | API host detail |
| 7 | VulnerabilitiesPage | P1 | API vulns |
| 8 | CampaignsPage | P1 | API campaigns |
| 9 | LoginPage | P1 | API auth |
| 10 | ReportsPage | P2 | API reports |
| 11 | VulnDetailPage | P2 | API vuln detail |
| 12 | CampaignDetailPage | P2 | API campaign detail |
| 13 | Components réutilisables | P0 | — |

---

## API contract (Backend → Frontend)

### Endpoints attendus pour Phase 1

```
GET    /api/v1/hosts              → { hosts: [...], total: int }
GET    /api/v1/hosts/:id          → { host: {...}, services: [...] }
GET    /api/v1/services           → { services: [...], total: int }
GET    /api/v1/services/:id       → { service: {...} }
GET    /api/v1/vulnerabilities    → { vulnerabilities: [...], total: int }
GET    /api/v1/vulnerabilities/:id → { vulnerability: {...}, mitre_techniques: [...] }
GET    /api/v1/dashboard/stats    → { hosts: int, services: int, vulns: int, by_severity: {...} }
POST   /api/v1/auth/login         → { access_token, token_type }
POST   /api/v1/campaigns          → { campaign: {...} }
GET    /api/v1/campaigns          → { campaigns: [...], total: int }
GET    /api/v1/campaigns/:id      → { campaign: {...}, results: [...] }
```

Tous les endpoints retournent `{ "detail": "..." }` en cas d'erreur.

---

## Règles de développement

1. **Composants atomiques** : un fichier = un composant, < 300 lignes
2. **Composition API** : utiliser `<script setup>` partout
3. **Tailwind uniquement** : pas de CSS personnalisé (sauf directives @apply dans style.css)
4. **Responsive first** : mobile → desktop
5. **État vide** : chaque liste doit gérer le cas "aucune donnée"
6. **Loading** : chaque page affiche un spinner pendant le chargement
7. **Erreur API** : toast notification en cas d'erreur
8. **i18n** : libellés en français

---

*Document généré le 2026-06-03. Mis à jour par l'orchestrateur.*
