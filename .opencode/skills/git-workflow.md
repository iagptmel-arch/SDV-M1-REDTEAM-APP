# Git Workflow

## Conventions commits
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `refactor:` refactoring sans changement fonctionnel
- `docs:` documentation uniquement
- `test:` ajout ou modification de tests
- `chore:` maintenance (deps, config)

## Branches
- `main` : production stable
- `develop` : intégration
- `feat/<nom>` : nouvelle fonctionnalité
- `fix/<nom>` : correction

## Règles
- Une fonctionnalité = une branche dédiée
- Review obligatoire (code-reviewer) avant merge sur develop
- Push après chaque fonctionnalité validée et testée
- Jamais de credentials dans les commits
