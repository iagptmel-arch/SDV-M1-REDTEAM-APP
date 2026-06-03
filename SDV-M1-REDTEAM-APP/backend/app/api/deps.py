"""
Dépendances partagées pour les endpoints API
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valide le token JWT et retourne l'utilisateur courant."""
    token = credentials.credentials
    # TODO: implémenter la validation JWT
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou manquant",
        )
    return token
