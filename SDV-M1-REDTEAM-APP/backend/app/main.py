"""
Application de découverte et d'analyse réseau
Point d'entrée FastAPI
"""

from fastapi import FastAPI

app = FastAPI(
    title="SDV-M1-REDTEAM-APP",
    description="Application de découverte et d'analyse réseau",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
