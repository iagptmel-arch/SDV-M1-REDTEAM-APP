"""
Configuration centralisée de l'application
"""

import logging
import os

logger = logging.getLogger(__name__)


class Settings:
    PROJECT_NAME: str = "SDV-M1-REDTEAM-APP"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "redteam_app")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()

if not settings.SECRET_KEY:
    import secrets
    settings.SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "SECRET_KEY non définie en environnement. "
        "Utilisation d'une clé générée aléatoirement. "
        "Les sessions seront invalidées au redémarrage."
    )
