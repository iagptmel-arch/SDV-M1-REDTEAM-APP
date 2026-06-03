# MongoDB — Patterns projet

## Collections
- `hosts` : hôtes découverts
- `scans` : historique des campagnes de scan
- `ports` : ports ouverts par hôte
- `vulnerabilities` : CVE identifiées
- `auth_tests` : résultats tests d'authentification
- `reports` : rapports générés

## Règles
- Toujours utiliser Motor (async) — jamais PyMongo synchrone dans FastAPI
- Index obligatoires sur `host_id`, `scan_id`, `cve_id`
- Timestamps `created_at` / `updated_at` sur tous les documents
- Jamais de requêtes avec `{}` en production (full scan interdit)

## Pattern type
```python
async def get_host(db, host_id: str):
    return await db.hosts.find_one({"_id": ObjectId(host_id)})
```
