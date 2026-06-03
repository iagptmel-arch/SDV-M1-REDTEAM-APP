"""
Schémas de validation pour les hôtes
"""

from ipaddress import IPv4Address, ip_address

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class HostCreate(BaseModel):
    ip: str
    hostname: Optional[str] = None

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        try:
            ip_address(v)
        except ValueError:
            raise ValueError(f"IP invalide : {v}")
        return v


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
