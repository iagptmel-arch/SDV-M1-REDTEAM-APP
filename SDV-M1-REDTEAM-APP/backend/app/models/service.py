"""
Modèle MongoDB pour les services détectés
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Service(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    host_id: str
    port: int
    protocol: str  # tcp / udp
    name: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    campaign_id: Optional[str] = None
