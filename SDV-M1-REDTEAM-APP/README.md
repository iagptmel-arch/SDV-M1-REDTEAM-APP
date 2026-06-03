# SDV-M1-REDTEAM-APP

Application de découverte et d'analyse réseau destinée à automatiser les
différentes phases d'identification des services exposés, d'analyse des
vulnérabilités et de validation d'accès dans un cadre d'audit de sécurité
autorisé.

---

## Architecture

```
├── backend/          # API FastAPI (Python)
├── frontend/         # interface utilisateur (Vue 3 + Tailwind CSS)
├── docker/           # Docker Compose (dev / prod)
└── README.md
```

### Backend

- **Framework** : FastAPI (Python 3.12)
- **Base de données** : MongoDB (via Motor)
- **Authentification** : JWT (python-jose + passlib)
- **Tests** : pytest + httpx

### Frontend

- **Framework** : Vue 3 (Composition API)
- **Build** : Vite
- **Styling** : Tailwind CSS
- **Routing** : Vue Router

---

## Prérequis

- Docker et Docker Compose (recommandé)
- Python 3.12+ (développement local)
- Node.js 20+ (développement frontend)

---

## Démarrage rapide

### Avec Docker

```bash
# Démarrer l'ensemble des services
docker compose -f docker/docker-compose.yml up -d

# Mode développement (avec rechargement automatique)
docker compose -f docker/docker-compose.dev.yml up -d
```

L'API est accessible sur `http://localhost:8000`.
L'interface web est accessible sur `http://localhost:5173` (dev) ou `http://localhost` (prod).

### Développement local (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Développement local (frontend)

```bash
cd frontend
npm install
npm run dev
```

---

## Documentation API

Une fois le backend démarré :

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

---

## Fonctionnalités (Phases)

| Phase | Description |
|-------|-------------|
| 1 | Découverte réseau, scan de ports, banner grabbing, analyse de vulnérabilités (CVE), mapping MITRE ATT&CK |
| 2 | Tests d'authentification autorisés sur les services exposés (SSH, FTP, SMB, RDP, etc.) |
| 3 | Automatisation complète du workflow, planification, rapports PDF/CSV/JSON |

---

## Licence

Projet académique — M1 REDTEAM.
