"""
Schémas de validation pour les campagnes
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    targets: list[str] = []


class CampaignRead(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    targets: list[str]
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    summary: Optional[dict] = None
    error: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    targets: Optional[list[str]] = None
    status: Optional[str] = None
