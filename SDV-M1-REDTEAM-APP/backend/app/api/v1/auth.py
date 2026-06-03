"""
Endpoints d'authentification
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login():
    """Authentification utilisateur."""
    return {"message": "login endpoint"}


@router.post("/register")
async def register():
    """Inscription utilisateur."""
    return {"message": "register endpoint"}
