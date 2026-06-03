# Plan de projet — SDV-M1-REDTEAM-APP

Application de découverte et d'analyse réseau.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3 + Tailwind)           │
│  Dashboard | Hosts | Services | Vulns | Campaigns | Rep.│
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP REST (JSON)
┌──────────────────────▼───────────────────────────────────┐
│                 Backend (FastAPI / Python)               │
│  api/v1/: hosts | services | vulns | campaigns | auth    │
│  services/: discovery | scanner | banner | vuln | mitre  │
│            auth_test | report                            │
│  core/: config | database (Motor) | security (JWT)       │
└──────────────────────┬───────────────────────────────────┘
                       │ Async (Motor)
┌──────────────────────▼───────────────────────────────────┐
│                    MongoDB (7)                           │
│  hosts | services | vulnerabilities | campaigns | users   │
└──────────────────────────────────────────────────────────┘
```

---

## Phases de développement

### Phase 1 : Découverte et collecte d'informations
*Période* : J1 à J30 | *Milestone* : #1 | **Statut** : ✅ Terminée

| # | Tâche | Priorité | Issues | Statut |
|---|-------|----------|--------|--------|
| 1 | Module de découverte réseau (ping sweep, ARP) | Haute | #3 | ✅ |
| 2 | Scan ports TCP/UDP | Haute | #4 | ✅ |
| 3 | Identification des services exposés | Haute | #5 | ✅ |
| 4 | Banner grabbing | Haute | #6 | ✅ |
| 5 | Détection des systèmes d'exploitation | Moyenne | #7 | ✅ |
| 6 | Analyse de vulnérabilités (CVE lookup) | Haute | #8 | ✅ |
| 7 | Mapping MITRE ATT&CK | Haute | #9 | ✅ |
| 8 | Modèles MongoDB et stockage | Haute | #10 | ✅ |
| 9 | API endpoints Phase 1 | Haute | #11 | ✅ |
| 10 | Frontend : découverte et inventaire | Haute | #12 | ✅ |
| 11 | Frontend : vulnérabilités et MITRE | Moyenne | #13 | ✅ |
| 12 | Tests Phase 1 | Moyenne | #14 | ✅ |

**Services backend impliqués** : `discovery.py`, `scanner.py`, `banner.py`, `vulnerability.py`, `mitre.py`
**Endpoints API** : `/api/v1/hosts/*`, `/api/v1/services/*`, `/api/v1/vulnerabilities/*`, `/api/v1/campaigns/*`

---

### Phase 2 : Validation d'accès sur services exposés
*Période* : J31 à J60 | *Milestone* : #2

| # | Tâche | Priorité | Issues |
|---|-------|----------|--------|
| 1 | Module d'authentification SSH | Haute | #15 |
| 2 | Module d'authentification FTP | Haute | #16 |
| 3 | Module d'authentification SMB | Haute | #17 |
| 4 | Module d'authentification Telnet | Haute | #18 |
| 5 | Module d'authentification RDP | Haute | #19 |
| 6 | Gestion des identifiants de test | Haute | #20 |
| 7 | Journalisation complète des tests | Haute | #21 |
| 8 | Génération de rapports détaillés | Haute | #22 |
| 9 | API endpoints Phase 2 | Haute | #23 |
| 10 | Frontend : tests d'accès | Haute | #24 |
| 11 | Tests Phase 2 | Haute | #25 |

**Services backend impliqués** : `auth_test.py`, `report.py`
**Services testés** : SSH (22), FTP (21), SMB (445), Telnet (23), RDP (3389)

---

### Phase 3 : Automatisation du workflow
*Période* : J61 à J90 | *Milestone* : #3

| # | Tâche | Priorité | Issues |
|---|-------|----------|--------|
| 1 | Pipeline de traitement automatisé | Haute | #26 |
| 2 | Planification des campagnes (scheduler) | Haute | #27 |
| 3 | Gestion multi-cibles et groupes | Haute | #28 |
| 4 | Tableau de bord centralisé | Haute | #29 |
| 5 | Notifications d'événements | Moyenne | #30 |
| 6 | Export PDF/CSV/JSON | Haute | #31 |
| 7 | Recherche et filtrage avancés | Moyenne | #32 |
| 8 | Comparaison entre campagnes | Moyenne | #33 |
| 9 | Frontend : dashboard et rapports | Haute | #34 |
| 10 | Tests Phase 3 | Haute | #35 |

**Pipeline complet** : Découverte → Scan → Services → Bannières → CVE → MITRE → Auth → Rapport

---

### Cross-cutting & Infrastructure
*Période* : Continue | *Milestone* : #4

| # | Tâche | Priorité | Issues |
|---|-------|----------|--------|
| CC-1 | Authentification utilisateur (JWT) | Haute | #36 |
| CC-2 | Gestion des rôles et permissions (RBAC) | Haute | #37 |
| CC-3 | Documentation technique | Moyenne | #38 |
| CC-4 | Documentation d'installation | Moyenne | #39 |
| CC-5 | Documentation API (Swagger/OpenAPI) | Haute | #40 |
| INF-1 | Docker et Docker Compose | Haute | #41 |
| INF-2 | CI/CD (GitHub Actions) | Haute | #42 |
| INF-3 | Tests automatisés et couverture | Haute | #43 |
| INF-4 | Sécurité : hardening et conformité | Haute | #44 |
| INF-5 | Script GH Project updater | Moyenne | #45 |

---

## Workflow de développement

### Branches
```
master
├── feat/init-structure          ← Structure initiale (faite)
├── feat/p1-discovery            ← Phase 1
├── feat/p1-scan-ports
├── feat/p1-banner-grabbing
├── feat/p1-cve-analysis
├── feat/p1-mitre-mapping
├── feat/p2-auth-ssh
├── feat/p2-auth-ftp
├── feat/p2-auth-smb
├── feat/p2-reporting
├── feat/p3-pipeline
├── feat/p3-scheduler
├── feat/p3-dashboard
├── feat/ci-cd
├── feat/fix-integration        ← Intégration MongoDB réelle (faite)
└── feat/documentation
```

### Règles
1. **Une fonctionnalité = une branche dédiée**
2. **Review obligatoire** par `code-reviewer` avant merge
3. **Commits explicites** et fréquents
4. **Push systématique** après chaque fonctionnalité testée
5. **Tests avant merge** (CI ou local)

### Sous-agents spécialisés
| Agent | Rôle |
|-------|------|
| `backend-dev` | Implémentation backend (FastAPI, MongoDB, services) |
| `frontend-dev` | Interface utilisateur (Vue 3, Tailwind) |
| `security-analyst` | Audit sécurité, conformité, CVE |
| `devops-engineer` | Docker, CI/CD, déploiement |
| `code-reviewer` | Review de code avant merge |

---

## GitHub Project

- **URL** : https://github.com/users/iagptmel-arch/projects/1
- **Colonnes** : Todo → In Progress → Review → Done
- **Champs** : Phase, Priority, Story Points
- **Labels** : `phase-1`, `phase-2`, `phase-3`, `cross-cutting`, `infrastructure`
- **Priorités** : `priority-critical`, `priority-high`, `priority-medium`, `priority-low`

### Mise à jour automatique par les agents
```bash
# Ajouter une issue
./scripts/gh-project-updater.sh add-issue "Titre" phase-1 "Phase 1: Découverte & collecte"

# Changer le statut
./scripts/gh-project-updater.sh update-status 42 "In Progress"

# Déplacer de phase
./scripts/gh-project-updater.sh move-phase 42 "Phase 2"
```

---

## Livrables finaux

- [x] Backend FastAPI documenté
- [x] Base MongoDB opérationnelle
- [x] Interface web responsive (Tailwind CSS)
- [x] Documentation technique complète (README, USAGE, PLAN, UI-PLAN)
- [x] Documentation d'installation
- [x] Documentation API (Swagger/OpenAPI disponible sur /docs)
- [x] Tests unitaires et d'intégration (44/44)
- [x] Déploiement via Docker et Docker Compose
- [x] Tableau de bord opérationnel
- [x] Gestion du projet via GitHub Projects (43 issues, 4 milestones)

---

*Généré le 2026-06-03 — Mise à jour via les agents automatisée via `scripts/gh-project-updater.sh`*
