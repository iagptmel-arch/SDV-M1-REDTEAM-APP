"""
Schémas de validation pour les services
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServiceCreate(BaseModel):
    host_id: str
    port: int
    protocol: str
    name: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None


class ServiceRead(BaseModel):
    id: str
    host_id: str
    port: int
    protocol: str
    name: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    discovered_at: datetime
    campaign_id: Optional[str] = None
