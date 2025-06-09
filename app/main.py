# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from app.db import init_db, db

app = FastAPI(title="Servicio: Publicar Oferta")

# Inicializamos la conexión a MongoDB al arrancar
init_db(app)


# --- Modelo Pydantic para Oferta (datos entrantes) ---
class OfertaIn(BaseModel):
    titulo: str = Field(..., min_length=5, description="Título mínimo 5 caracteres")
    descripcion: str = Field(..., min_length=20, description="Descripción mínimo 20 caracteres")
    categoria: str = Field(..., description="Categoría (p.ej. 'Plomería', 'Electricidad', etc.)")
    horario: str = Field(..., description="Horario en que el proveedor está disponible")

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Reparación de tubería de cocina",
                "descripcion": "Necesito un plomero que repare una fuga en la tubería de la cocina, preferiblemente entre semana de 3pm a 6pm.",
                "categoria": "Plomería",
                "horario": "Lun–Vie 15:00–18:00"
            }
        }


# --- Modelo Pydantic para Oferta (datos salientes, con _id convertido a string) ---
class OfertaOut(BaseModel):
    id: str = Field(..., alias="_id")             # Aquí recibiremos _id como str
    titulo: str
    descripcion: str
    categoria: str
    horario: str
    reputacion: float = Field(0.0, description="Reputación inicial del proveedor")

    class Config:
        model_config = { "populate_by_name": True }  # Permite usar el alias "_id"


# --- Endpoint raíz de prueba ---
@app.get("/")
async def read_root():
    return {"mensaje": "API de Publicar Oferta funcionando"}


# --- Endpoint para comprobar que la API está arriba ---
@app.get("/status")
async def status():
    return {"status": "OK"}


# --- Crear nueva oferta ---
@app.post("/ofertas", response_model=OfertaOut, status_code=201)
async def crear_oferta(oferta: OfertaIn):
    oferta_dict = oferta.dict()
    oferta_dict["reputacion"] = 0.0

    # 1. Insertamos en MongoDB
    result = await db.ofertas.insert_one(oferta_dict)

    # 2. Buscamos la oferta recién creada
    nuevo = await db.ofertas.find_one({"_id": result.inserted_id})
    if not nuevo:
        raise HTTPException(status_code=500, detail="Error al crear la oferta")

    # 3. Convertimos el ObjectId a str para que Pydantic lo acepte como 'id'
    nuevo["_id"] = str(nuevo["_id"])
    return nuevo


# --- Listar todas las ofertas (sin filtros, paginación simple) ---
@app.get("/ofertas", response_model=List[OfertaOut])
async def listar_ofertas():
    cursor = db.ofertas.find()
    ofertas = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])   # Convertimos cada ObjectId a str
        ofertas.append(doc)
    return ofertas
