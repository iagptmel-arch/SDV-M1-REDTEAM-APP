"""
Connexion MongoDB et fonctions CRUD génériques
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_db():
    """Initialise la connexion MongoDB."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]


async def close_db():
    """Ferme la connexion MongoDB."""
    global client
    if client:
        client.close()


def get_db():
    """Retourne l'instance de la base de données."""
    return db


async def insert_one(collection: str, data: dict) -> str:
    """Insère un document et retourne son ID."""
    result = await db[collection].insert_one(data)
    return str(result.inserted_id)


async def find_many(
    collection: str,
    query: dict | None = None,
    skip: int = 0,
    limit: int = 100,
    sort: list[tuple] | None = None,
) -> list[dict]:
    """Retourne une liste paginée de documents."""
    cursor = db[collection].find(query or {}).skip(skip).limit(limit)
    if sort:
        cursor = cursor.sort(sort)
    return await cursor.to_list(length=limit)


async def find_one(collection: str, query: dict) -> dict | None:
    """Retourne un document unique."""
    return await db[collection].find_one(query)


async def update_one(collection: str, query: dict, data: dict) -> bool:
    """Met à jour un document. Retourne True si modifié."""
    result = await db[collection].update_one(query, {"$set": data})
    return result.modified_count > 0


async def delete_one(collection: str, query: dict) -> bool:
    """Supprime un document. Retourne True si supprimé."""
    result = await db[collection].delete_one(query)
    return result.deleted_count > 0


async def count(collection: str, query: dict | None = None) -> int:
    """Compte les documents correspondant à la requête."""
    return await db[collection].count_documents(query or {})
