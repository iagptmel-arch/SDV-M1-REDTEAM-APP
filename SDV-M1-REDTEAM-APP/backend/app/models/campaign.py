"""
Modèle MongoDB pour les campagnes d'analyse
"""

from pydantic import BaseModel, Field
from typing import Optional, list
from datetime import datetime


class Campaign(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None
    targets: list[str] = []
    status: str = "draft"  # draft / running / completed / failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None
