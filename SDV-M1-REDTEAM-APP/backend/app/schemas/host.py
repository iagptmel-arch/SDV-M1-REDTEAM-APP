"""
Schémas de validation pour les hôtes
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HostCreate(BaseModel):
    ip: str
    hostname: Optional[str] = None


class HostRead(BaseModel):
    id: str
    ip: str
    hostname: Optional[str] = None
    os: Optional[str] = None
    status: str
    discovered_at: datetime
    campaign_id: Optional[str] = None


class HostUpdate(BaseModel):
    hostname: Optional[str] = None
    os: Optional[str] = None
    status: Optional[str] = None
