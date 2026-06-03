# Procédure d'utilisation — SDV-M1-REDTEAM-APP

Guide pas à pas pour installer, configurer et utiliser l'application de
découverte et d'analyse réseau.

---

## Table des matières

1. [Installation](#1-installation)
2. [Première connexion](#2-première-connexion)
3. [Créer un compte administrateur](#3-créer-un-compte-administrateur)
4. [Ajouter des hôtes manuellement](#4-ajouter-des-hôtes-manuellement)
5. [Lancer une découverte réseau](#5-lancer-une-découverte-réseau)
6. [Scanner les ports d'un hôte](#6-scanner-les-ports-dun-hôte)
7. [Analyser les vulnérabilités](#7-analyser-les-vulnérabilités)
8. [Consulter le mapping MITRE ATT&CK](#8-consulter-le-mapping-mitre-attck)
9. [Créer et gérer des campagnes](#9-créer-et-gérer-des-campagnes)
10. [Générer des rapports](#10-générer-des-rapports)
11. [API REST (curl / PowerShell)](#11-api-rest-curl--powershell)
12. [Dépannage](#12-dépannage)

---

## 1. Installation

### 1.1 Prérequis

- Docker et Docker Compose installés
- Ou Python 3.12+ et Node.js 20+ (développement local)

### 1.2 Lancement avec Docker

```bash
# Cloner le dépôt
git clone https://github.com/iagptmel-arch/SDV-M1-REDTEAM-APP.git
cd SDV-M1-REDTEAM-APP

# Démarrer les services (mode production)
docker compose -f docker/docker-compose.yml up -d

# Vérifier que tout est opérationnel
docker compose -f docker/docker-compose.yml ps

# Consulter les logs
docker compose -f docker/docker-compose.yml logs -f
```

### 1.3 Mode développement (hot-reload)

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

### 1.4 Vérifier que l'API répond

```bash
curl http://localhost:8000/health
# Réponse attendue : {"status":"ok"}
```

### 1.5 Accès aux interfaces

| Service | URL |
|---------|-----|
| Interface web (prod) | http://localhost |
| Interface web (dev) | http://localhost:5173 |
| API REST | http://localhost:8000 |
| Documentation Swagger | http://localhost:8000/docs |
| Documentation ReDoc | http://localhost:8000/redoc |

---

## 2. Première connexion

### Via l'interface web

1. Ouvrir http://localhost (ou http://localhost:5173 en dev)
2. Vous êtes redirigé vers la page de connexion `/login`
3. Cliquer sur le lien **"Créer un compte"** si vous n'en avez pas encore

### Via l'API

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"changeme","role":"admin"}'
```

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```

La réponse contient un token JWT à utiliser pour les requêtes authentifiées :

```json
{"access_token":"eyJ...","token_type":"bearer"}
```

---

## 3. Créer un compte administrateur

Le rôle **admin** permet de :
- Créer, modifier, supprimer des hôtes, services, vulnérabilités, campagnes
- Lancer des découvertes et scans
- Gérer les autres utilisateurs

```bash
# Création via l'API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "VotreMotDePasseFort!",
    "role": "admin"
  }'
```

> **Important** : Changez le mot de passe après la première connexion.
> Le mot de passe doit contenir au moins 8 caractères.

---

## 4. Ajouter des hôtes manuellement

### Via l'interface web

1. Aller dans **Hôtes** (`/hosts`)
2. Cliquer sur **"Ajouter un hôte"** (bouton en haut à droite)
3. Renseigner l'adresse IP (ex: `192.168.1.10`) et optionnellement le hostname
4. Valider

### Via l'API

```bash
# Ajouter un hôte
curl -X POST http://localhost:8000/api/v1/hosts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -d '{"ip": "192.168.1.10", "hostname": "serveur-web"}'

# Ajouter plusieurs hôtes
for ip in 192.168.1.{10..20}; do
  curl -X POST http://localhost:8000/api/v1/hosts \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer VOTRE_TOKEN" \
    -d "{\"ip\": \"$ip\"}"
done
```

---

## 5. Lancer une découverte réseau

La découverte réseau utilise une combinaison de :
- **ICMP ping sweep** (détection des hôtes actifs)
- **ARP scan** (détection sur le réseau local, nécessite `arp-scan`)
- **TCP SYN** sur quelques ports communs (22, 80, 443)

### Via l'API (recommandé pour les analyses)

```python
# Exemple Python
import requests

API = "http://localhost:8000/api/v1"
TOKEN = "VOTRE_TOKEN"

# 1. Découvrir les hôtes sur le réseau 192.168.1.0/24
response = requests.post(f"{API}/discovery/scan", json={
    "target": "192.168.1.0/24"
}, headers={"Authorization": f"Bearer {TOKEN}"})

# 2. Les hôtes découverts sont automatiquement stockés
# 3. Les consulter
hosts = requests.get(f"{API}/hosts", headers={"Authorization": f"Bearer {TOKEN}"})
print(hosts.json())
```

> **Note** : La découverte réseau est disponible via le service Python
> `backend/app/services/discovery.py`. L'endpoint API dédié sera ajouté
> dans les phases suivantes. Pour l'instant, vous pouvez l'utiliser
> directement en Python.

### Utilisation du service en Python

```python
import asyncio
from app.services.discovery import discover_hosts

async def scan():
    hosts = await discover_hosts("192.168.1.0/24")
    for h in hosts:
        print(f"✓ {h['ip']} - {h.get('hostname', 'N/A')} ({h['method']})")

asyncio.run(scan())
```

---

## 6. Scanner les ports d'un hôte

### Via l'API

```python
import requests

API = "http://localhost:8000/api/v1"
TOKEN = "VOTRE_TOKEN"

# Scanner les ports d'un hôte
response = requests.post(f"{API}/scanner/scan", json={
    "host": "192.168.1.10",
    "ports": [22, 80, 443, 445, 3389],  # optionnel, 1000 ports par défaut
    "protocol": "tcp"
}, headers={"Authorization": f"Bearer {TOKEN}"})

services = response.json()
for s in services:
    print(f"Port {s['port']}/{s['protocol']} - {s.get('name', '?')} - {s.get('version', '?')}")
```

### Utilisation directe du service

```python
import asyncio
from app.services.scanner import scan_ports

async def scan():
    ports = await scan_ports("192.168.1.10", protocol="tcp")
    for p in ports[:10]:  # 10 premiers résultats
        print(f"  {p['port']}/{p['protocol']} {p['state']} - {p.get('name', '?')}")

asyncio.run(scan())
```

---

## 7. Analyser les vulnérabilités

L'analyse CVE interroge l'API publique NVD (National Vulnerability Database).

### Via l'API

```python
import requests

API = "http://localhost:8000/api/v1"
TOKEN = "VOTRE_TOKEN"

# Ajouter une vulnérabilité (après analyse)
response = requests.post(f"{API}/vulnerabilities", json={
    "service_id": "ID_DU_SERVICE",
    "cve_id": "CVE-2024-XXXXX",
    "description": "Description de la vulnérabilité",
    "severity": "high",
    "cvss_score": 7.5,
    "mitre_techniques": ["T1190"]
}, headers={"Authorization": f"Bearer {TOKEN}"})

# Lister les vulnérabilités avec filtre
vulns = requests.get(f"{API}/vulnerabilities", params={
    "severity": "critical"
}, headers={"Authorization": f"Bearer {TOKEN}"})
```

### Recherche automatique via le service Python

```python
import asyncio
from app.services.vulnerability import search_cves

async def analyze():
    cves = await search_cves("openssh", "8.9p1")
    for cve in cves:
        print(f"{cve['cve_id']} - {cve['severity']} ({cve['cvss_score']})")
        print(f"  {cve['description'][:100]}...")

asyncio.run(analyze())
```

---

## 8. Consulter le mapping MITRE ATT&CK

### Via l'interface web

1. Aller dans **Vulnérabilités** (`/vulnerabilities`)
2. Cliquer sur une vulnérabilité
3. La section **MITRE ATT&CK** affiche les techniques associées

### Via l'API

```bash
curl http://localhost:8000/api/v1/vulnerabilities/ID_VULN \
  -H "Authorization: Bearer VOTRE_TOKEN" | python3 -m json.tool
```

La réponse inclut les techniques MITRE :

```json
{
  "id": "...",
  "cve_id": "CVE-2024-XXXXX",
  "severity": "high",
  "mitre_techniques": [
    {
      "technique_id": "T1190",
      "technique_name": "Exploit Public-Facing Application",
      "tactic": "Initial Access",
      "description": "Adversaries may attempt to exploit a weakness in an Internet-facing computer..."
    }
  ]
}
```

### Mapping disponible

| Service | Techniques MITRE |
|---------|-----------------|
| SSH | T1021.004, T1110 |
| HTTP/HTTPS | T1190, T1071.001 |
| FTP | T1048 |
| SMB | T1021.002, T1550.002 |
| RDP | T1021.001, T1110 |
| Telnet | T1021.004, T1110 |
| SMTP | T1071.003 |
| DNS | T1071.004 |
| MySQL | T1213 |
| PostgreSQL | T1213 |

---

## 9. Créer et gérer des campagnes

### Via l'interface web

1. Aller dans **Campagnes** (`/campaigns`)
2. Cliquer sur **"Nouvelle campagne"**
3. Renseigner :
   - **Nom** : ex. "Audit réseau interne"
   - **Cibles** : séparées par des virgules (ex: `192.168.1.0/24,10.0.0.0/8`)
   - **Description** (optionnelle)
4. Valider

### Via l'API

```bash
# Créer une campagne
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -d '{
    "name": "Audit réseau interne",
    "targets": ["192.168.1.0/24", "10.0.0.0/8"],
    "description": "Scan complet du réseau interne"
  }'

# Lister les campagnes
curl http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

---

## 10. Générer des rapports

> **Note** : La génération de rapports PDF/CSV/JSON sera disponible
> en Phase 3. Les endpoints API et l'interface sont préparés.

Pour l'instant, vous pouvez exporter les données manuellement :

```bash
# Exporter les hôtes en JSON
curl http://localhost:8000/api/v1/hosts?limit=500 \
  -H "Authorization: Bearer VOTRE_TOKEN" > hosts_export.json

# Exporter les services en CSV (via jq)
curl http://localhost:8000/api/v1/services?limit=500 \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  | jq -r '.[] | [.port, .protocol, .name, .version] | @csv' > services.csv
```

---

## 11. API REST (curl / PowerShell)

### curl (Linux/macOS)

```bash
# Variables
TOKEN="eyJ..."
API="http://localhost:8000/api/v1"
AUTH="Authorization: Bearer $TOKEN"

# Dashboard
curl -s $API/dashboard/stats -H "$AUTH" | jq .

# Hôtes
curl -s "$API/hosts?limit=10&status=up" -H "$AUTH" | jq '.'
curl -s $API/hosts/ID_HOTE -H "$AUTH" | jq '.'

# Services
curl -s "$API/services?protocol=tcp&port_min=1&port_max=1024" -H "$AUTH" | jq '.'

# Vulnérabilités
curl -s "$API/vulnerabilities?severity=critical" -H "$AUTH" | jq '.'
```

### PowerShell (Windows)

```powershell
$token = "eyJ..."
$api = "http://localhost:8000/api/v1"
$headers = @{ Authorization = "Bearer $token" }

# Dashboard
Invoke-RestMethod -Uri "$api/dashboard/stats" -Headers $headers | ConvertTo-Json

# Hôtes
Invoke-RestMethod -Uri "$api/hosts?limit=10" -Headers $headers | ConvertTo-Json

# Créer une campagne
$body = @{
    name = "Scan PowerShell"
    targets = @("192.168.1.0/24")
    description = "Campagne depuis PowerShell"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$api/campaigns" -Method Post -Body $body `
    -ContentType "application/json" -Headers $headers | ConvertTo-Json
```

### Python

```python
import requests

API = "http://localhost:8000/api/v1"
TOKEN = "VOTRE_TOKEN"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Dashboard
stats = requests.get(f"{API}/dashboard/stats", headers=HEADERS).json()
print(f"Hôtes : {stats['hosts']}")
print(f"Services : {stats['services']}")
print(f"Vulnérabilités : {stats['vulnerabilities']}")
print(f"Répartition : {stats['by_severity']}")

# Liste paginée des hôtes
page = 1
while True:
    resp = requests.get(f"{API}/hosts?skip={(page-1)*20}&limit=20", headers=HEADERS)
    hosts = resp.json()
    if not hosts:
        break
    print(f"\nPage {page} :")
    for h in hosts:
        print(f"  {h['ip']} - {h.get('hostname', 'N/A')} [{h['status']}]")
    page += 1
```

---

## 12. Dépannage

### Problèmes courants

| Problème | Cause probable | Solution |
|----------|---------------|----------|
| `curl: Connection refused` | API non démarrée | Vérifier `docker ps` |
| `401 Unauthorized` | Token manquant ou invalide | Refaire un login |
| `409 Conflict` (hôte) | IP déjà existante | Utiliser une IP différente |
| `404 Not Found` | ID inexistant | Vérifier l'ID dans la liste |
| MongoDB connection error | MongoDB non accessible | Vérifier `docker compose logs mongo` |
| `npm install` échoue | Node.js pas installé | Installer Node.js 20+ |

### Vérifier l'état des services

```bash
# État des conteneurs
docker compose -f docker/docker-compose.yml ps

# Logs de l'API
docker compose -f docker/docker-compose.yml logs backend

# Logs MongoDB
docker compose -f docker/docker-compose.yml logs mongo

# Tester la connexion MongoDB
docker exec -it redteam-mongo mongosh --eval "db.runCommand({ping:1})"
```

### Réinitialiser la base de données

```bash
# Supprimer les volumes (⚠️ perd toutes les données)
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d
```

### Exécuter les tests backend

```bash
cd backend
python -m pytest tests/ -v
# 44 tests doivent passer
```

---

## Workflow de développement

```bash
# 1. Créer une branche pour une fonctionnalité
git checkout -b feat/ma-fonctionnalite feat/init-structure

# 2. Développer
# ...

# 3. Exécuter les tests
python -m pytest backend/tests/ -v

# 4. Commit et push
git add .
git commit -m "feat: description de la fonctionnalité"
git push origin feat/ma-fonctionnalite

# 5. Créer une Pull Request sur GitHub
```

---

## Références

- **Documentation API** : http://localhost:8000/docs (une fois l'API démarrée)
- **Plan de projet** : [PLAN.md](PLAN.md)
- **Architecture UI** : [UI-PLAN.md](UI-PLAN.md)
- **GitHub Project** : https://github.com/users/iagptmel-arch/projects/1

---

*Document mis à jour le 2026-06-03 — SDV-M1-REDTEAM-APP Phase 1*
