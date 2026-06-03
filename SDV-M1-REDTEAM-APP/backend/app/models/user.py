"""
Modèle MongoDB pour les utilisateurs
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    hashed_password: str
    role: str = "viewer"  # admin / analyst / viewer
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
