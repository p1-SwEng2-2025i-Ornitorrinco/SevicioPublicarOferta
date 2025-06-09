# app/main.py
from fastapi import FastAPI
from app.db import init_db
from pydantic import BaseModel, Field

app = FastAPI(title="Servicio: Publicar Oferta")

# Inicializa la conexión a MongoDB al arrancar
init_db(app)

# Ejemplo de modelo (más adelante lo ampliaremos)
class Oferta(BaseModel):
    titulo: str = Field(..., min_length=5)
    descripcion: str = Field(..., min_length=20)
    categoria: str
    horario: str

@app.get("/")
async def read_root():
    return {"mensaje": "API de Publicar Oferta funcionando"}

# Ruta de prueba para verificar que FastAPI está vivo
@app.get("/status")
async def status():
    return {"status": "OK"}
