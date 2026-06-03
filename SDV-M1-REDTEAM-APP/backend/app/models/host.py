"""
Modèle MongoDB pour les hôtes découverts
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Host(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    ip: str
    hostname: Optional[str] = None
    os: Optional[str] = None
    status: str = "unknown"  # up / down / unknown
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    campaign_id: Optional[str] = None
