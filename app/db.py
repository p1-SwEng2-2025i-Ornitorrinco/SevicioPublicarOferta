# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

client = None
db = None

def init_db(app: FastAPI):
    global client, db
    # Cambia la URI según tu configuración local o Atlas
    MONGO_URI = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["servicios_app"]
    # Siempre registra el cierre al apagar la app
    @app.on_event("shutdown")
    async def close_db():
        client.close()
