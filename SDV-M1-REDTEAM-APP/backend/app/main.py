"""
Application de découverte et d'analyse réseau
Point d'entrée FastAPI
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import connect_db, close_db, get_db
from app.api.v1.hosts import router as hosts_router
from app.api.v1.services import router as services_router
from app.api.v1.vulnerabilities import router as vulnerabilities_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="SDV-M1-REDTEAM-APP",
    description="Application de découverte et d'analyse réseau",
    version="0.1.0",
    lifespan=lifespan,
)

# Configuration CORS (toutes origines en dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers API v1
app.include_router(hosts_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")
app.include_router(vulnerabilities_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    """Vérifie l'état de l'application et de la base de données."""
    db = get_db()
    db_status = "connected" if db is not None else "disconnected"
    if db is not None:
        try:
            # Ping MongoDB
            await db.command("ping")
            db_status = "connected"
        except Exception:
            db_status = "error"
    return {"status": "ok", "database": db_status}
