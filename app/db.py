# app/db.py

from motor.motor_asyncio import AsyncIOMotorClient

# 1. Cadena de conexión (ajústala a tu entorno; puede ser local o Atlas)
MONGO_URI = "mongodb://localhost:27017"

# 2. Creamos el cliente y la base de datos inmediatamente
client = AsyncIOMotorClient(MONGO_URI)
db = client["servicios_app"]

