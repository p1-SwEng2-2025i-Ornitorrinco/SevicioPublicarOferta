# app/models/oferta.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OfertaIn(BaseModel):
    titulo: str = Field(..., min_length=5)
    descripcion: str = Field(..., min_length=20)
    categoria: str = Field(..., description="Categoría del servicio")
    ubicacion: str = Field(..., description="Ubicación del servicio")
    palabras_clave: Optional[List[str]] = Field(
        None,
        description="Lista de palabras clave relevantes (opcional)"
    )
    costo: float = Field(..., gt=0)
    horario: Optional[str] = Field(
        None,
        description="Horario en que el proveedor está disponible (opcional)"
    )
    visible: Optional[bool] = Field(
        None,
        description="Si la oferta está visible (no se envía en el Form; siempre inicializamos en True)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Reparación de tubería",
                "descripcion": "Reparar fuga en tubería de cocina...",
                "categoria": "Plomería",
                "ubicacion": "Bogotá",
                # palabras_clave y horario pueden omitirse
                "costo": 50000.0
            }
        }
    }

class OfertaOut(BaseModel):
    id: str = Field(..., alias="_id")
    titulo: str
    descripcion: str
    categoria: str
    ubicacion: str
    palabras_clave: Optional[List[str]] = None
    costo: float
    horario: Optional[str] = None
    cliente_id: str
    cliente_nombre: str
    created_at: datetime
    imagen_url: Optional[str] = None
    visible: bool = Field(..., description="Si la oferta está visible para búsquedas")

    model_config = {"populate_by_name": True}

class OfertaOutPerfil(BaseModel):
    id: str = Field(..., alias="_id")
    titulo: str
    descripcion: str
    categoria: str
    ubicacion: str
    palabras_clave: Optional[List[str]] = None
    costo: float
    horario: Optional[str] = None
    imagen_url: Optional[str] = None
    created_at: datetime
    visible: bool = Field(..., description="Si la oferta está visible para búsquedas")

    model_config = {"populate_by_name": True}

class OfertaUpdate(BaseModel):
    # los mismos campos opcionales que OfertaIn (sin created_at ni cliente info)
    titulo: Optional[str] = Field(None, min_length=5)
    descripcion: Optional[str] = Field(None, min_length=20)
    categoria: Optional[str] = None
    ubicacion: Optional[str] = None
    palabras_clave: Optional[List[str]] = None
    costo: Optional[float] = Field(None, gt=0)
    horario: Optional[str] = None
    imagen_url: Optional[str] = None

    model_config = {"json_schema_extra": {"example": {}}}
