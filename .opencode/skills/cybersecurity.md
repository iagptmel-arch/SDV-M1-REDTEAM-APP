# Cybersécurité — Règles et contexte

## MITRE ATT&CK Navigator
URL locale : http://192.168.2.131:4200/

## Tactiques prioritaires du projet
- TA0043 Reconnaissance
- TA0001 Initial Access
- TA0007 Discovery

## Format CVE
- Sévérité CVSS v3 : critical ≥9 / high ≥7 / medium ≥4 / low <4
- Source : NVD API (https://services.nvd.nist.gov/rest/json/cves/2.0)

## Règles impératives
- Toujours valider le scope autorisé avant tout scan
- Journalisation complète de toutes les opérations
- Jamais de credentials en dur dans le code
- Validation des inputs avant exécution de commandes système
- Principe du moindre privilège sur toutes les opérations

## OWASP LLM Top 10
- LLM01 : Prompt Injection — valider tous les inputs avant tool calls
- LLM06 : Sensitive Information Disclosure — ne jamais exposer clés/tokens
