# SDV-M1-REDTEAM-APP

Application de découverte et d'analyse réseau destinée à automatiser les
différentes phases d'identification des services exposés, d'analyse des
vulnérabilités et de validation d'accès dans un cadre d'audit de sécurité
autorisé.

**Statut Phase 1** : ✅ Terminée — Découverte réseau, scan de ports, banner grabbing, analyse CVE, mapping MITRE ATT&CK, API REST, interface web complète.

---

## Architecture

```
SDV-M1-REDTEAM-APP/
├── backend/                    # API FastAPI (Python 3.12)
│   ├── app/
│   │   ├── api/v1/             # Endpoints REST (hosts, services, vulns, campaigns, auth, dashboard)
│   │   ├── core/               # Configuration, base de données, sécurité
│   │   ├── models/             # Modèles MongoDB (Host, Service, Vulnerability, Campaign, User)
│   │   ├── schemas/            # Validation Pydantic
│   │   ├── services/           # Métier (discovery, scanner, banner, vulnerability, mitre, auth_test, report)
│   │   └── utils/              # Logger
│   ├── tests/                  # 44 tests unitaires et d'intégration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Interface utilisateur (Vue 3 + Tailwind CSS)
│   ├── src/
│   │   ├── pages/              # 9 pages (Login, Dashboard, Hosts, HostDetail, Services, Vulns, VulnDetail, Campaigns, Reports)
│   │   ├── components/         # Layout (sidebar) + 7 composants communs réutilisables
│   │   ├── composables/        # useApi (wrapper API avec JWT)
│   │   ├── router/             # Routes avec garde d'authentification
│   │   └── api/                # Client HTTP
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── Dockerfile
├── docker/                     # Docker Compose (dev / prod)
├── scripts/
│   └── gh-project-updater.sh   # Mise à jour automatique du GitHub Project
├── PLAN.md                     # Plan de projet détaillé
├── UI-PLAN.md                  # Architecture UI complète
├── USAGE.md                    # Procédure d'utilisation
└── README.md
```

### Stack technique

| Couche | Technologie | Version |
|--------|------------|---------|
| Backend | FastAPI / Python | 3.12+ |
| API | REST JSON (Swagger/OpenAPI) | — |
| Base de données | MongoDB + Motor (async) | 7 |
| Authentification | JWT (python-jose + bcrypt) | — |
| Frontend | Vue 3 (Composition API) | 3.5+ |
| Build | Vite | 5.x |
| Styling | Tailwind CSS | 3.4+ |
| Graphiques | Chart.js + vue-chartjs | — |
| Container | Docker + Docker Compose | — |
| CI/CD | GitHub Actions (à venir) | — |

---

## Prérequis

- Docker et Docker Compose (recommandé)
- Python 3.12+ (développement local)
- Node.js 20+ (développement frontend)

---

## Démarrage rapide

### Avec Docker

```bash
# 1. Cloner le dépôt
git clone https://github.com/iagptmel-arch/SDV-M1-REDTEAM-APP.git
cd SDV-M1-REDTEAM-APP

# 2. Lancer tous les services
docker compose -f docker/docker-compose.yml up -d

# 3. Accéder à l'interface
# Frontend : http://localhost
# API       : http://localhost:8000
# Swagger   : http://localhost:8000/docs
```

### Mode développement (hot-reload)

```bash
docker compose -f docker/docker-compose.dev.yml up -d
# Frontend : http://localhost:5173
# API       : http://localhost:8000
```

### Développement local (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Lancer l'API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Exécuter les tests
python -m pytest tests/ -v
```

### Développement local (frontend)

```bash
cd frontend
npm install
npm run dev
# Accès : http://localhost:5173
```

---

## Documentation API

Une fois le backend démarré :

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

### Endpoints Phase 1

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/auth/register` | Création de compte |
| POST | `/api/v1/auth/login` | Connexion (retourne JWT) |
| GET | `/api/v1/dashboard/stats` | Statistiques globales |
| GET | `/api/v1/hosts` | Liste des hôtes (paginée, filtrable) |
| GET | `/api/v1/hosts/{id}` | Détail d'un hôte |
| POST | `/api/v1/hosts` | Ajouter un hôte |
| DELETE | `/api/v1/hosts/{id}` | Supprimer un hôte |
| GET | `/api/v1/services` | Liste des services (filtrable) |
| GET | `/api/v1/services/{id}` | Détail d'un service |
| POST | `/api/v1/services` | Ajouter un service |
| GET | `/api/v1/vulnerabilities` | Liste des vulnérabilités (filtrable) |
| GET | `/api/v1/vulnerabilities/{id}` | Détail avec techniques MITRE |
| POST | `/api/v1/vulnerabilities` | Ajouter une vulnérabilité |
| GET | `/api/v1/campaigns` | Liste des campagnes |
| GET | `/api/v1/campaigns/{id}` | Détail campagne |
| POST | `/api/v1/campaigns` | Créer une campagne |
| PATCH | `/api/v1/campaigns/{id}` | Mettre à jour une campagne |
| GET | `/api/v1/health` | Santé du service |

---

## Services métier (Phase 1)

### Découverte réseau (`discovery.py`)
- ICMP ping sweep
- ARP scan (via `arp-scan`)
- TCP SYN sur ports communs
- Résolution DNS des hostnames

### Scan de ports (`scanner.py`)
- Scan TCP (connect) et UDP
- 1000 ports les plus communs par défaut
- Parallélisme asynchrone (max 100 connexions simultanées)
- Timeout et gestion d'erreurs

### Banner grabbing (`banner.py`)
- HTTP/HTTPS (en-têtes)
- SSH, FTP, SMTP, POP3, IMAP (bannières brutes)
- Timeout paramétrable

### Analyse CVE (`vulnerability.py`)
- Interrogation API NVD (National Vulnerability Database)
- Cache des résultats (TTL 1 heure)
- Calcul du score CVSS et niveau de criticité

### Mapping MITRE ATT&CK (`mitre.py`)
- Table de correspondance pour 10 services courants
- Surcharge possible par CVE
- Techniques avec tactiques associées

---

## Interface utilisateur

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | Authentification JWT |
| Dashboard | `/` | Statistiques, graphique donut, dernières campagnes |
| Hôtes | `/hosts` | Liste paginée, filtre statut, recherche |
| Détail hôte | `/hosts/:id` | Infos hôte + services associés |
| Services | `/services` | Liste paginée, filtres protocole/port |
| Vulnérabilités | `/vulnerabilities` | Liste paginée, filtre sévérité |
| Détail vulnérabilité | `/vulnerabilities/:id` | Description CVE, score CVSS, techniques MITRE |
| Campagnes | `/campaigns` | Liste, création (modal) |
| Rapports | `/reports` | Export PDF/CSV/JSON (Phase 3) |

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
# Résultat : 44 passed (15 intégration, 29 unitaires)
```

---

## Fonctionnalités par phase

| Phase | Description | Statut |
|-------|-------------|--------|
| **1** | Découverte réseau, scan de ports, banner grabbing, analyse CVE, mapping MITRE ATT&CK, API, UI | ✅ Terminée |
| **2** | Tests d'authentification autorisés (SSH, FTP, SMB, Telnet, RDP) + reporting | 🔜 À venir |
| **3** | Automatisation complète, planification, dashboard, notifications, exports | 🔜 À venir |

---

## Projet GitHub

- **Board** : https://github.com/users/iagptmel-arch/projects/1
- **Plan détaillé** : [PLAN.md](PLAN.md)
- **Architecture UI** : [UI-PLAN.md](UI-PLAN.md)
- **Procédure d'utilisation** : [USAGE.md](USAGE.md)

---

## Licence

Projet académique — M1 REDTEAM.
