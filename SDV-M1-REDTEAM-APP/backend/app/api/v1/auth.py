"""
Endpoints d'authentification
"""

from fastapi import APIRouter, HTTPException, status

from app.core.database import find_one, insert_one
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, Token, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(data: LoginRequest):
    """Authentifie un utilisateur et retourne un token JWT."""
    user = await find_one("users", {"username": data.username})
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe invalide",
        )

    token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "viewer")}
    )
    return Token(access_token=token)


@router.post("/register", response_model=dict)
async def register(data: UserCreate):
    """Crée un nouveau compte utilisateur."""
    existing = await find_one(
        "users",
        {"$or": [{"username": data.username}, {"email": data.email}]},
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nom d'utilisateur ou email déjà utilisé",
        )

    user_dict = data.model_dump()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
    user_id = await insert_one("users", user_dict)
    return {
        "message": "Utilisateur créé avec succès",
        "user_id": user_id,
        "username": data.username,
    }
