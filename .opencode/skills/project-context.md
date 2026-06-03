# Contexte projet

Application de découverte et d'analyse réseau pour audit de sécurité autorisé.

## Stack
- Backend : Python 3.11+, FastAPI, MongoDB (Motor async), Pydantic v2
- Frontend : HTML5, Tailwind CSS, JavaScript vanilla
- Infra : Docker, Docker Compose
- Versioning : GitHub, GitHub Projects

## Architecture
```
app/
├── api/routes/    # Routes FastAPI (thin — délèguent aux services)
├── services/      # Logique métier
├── models/        # Schémas Pydantic
├── db/            # Connexion MongoDB
└── core/          # Config, logging, settings
frontend/
├── pages/
├── components/
└── assets/
```

## Phases
1. Découverte réseau (nmap, banner grabbing, CVE, MITRE ATT&CK)
2. Tests d'authentification autorisés (SSH, FTP, SMB, RDP, Telnet)
3. Automatisation workflow + reporting (PDF, CSV, JSON)
