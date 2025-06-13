from pydantic import BaseModel, Field
from typing import List, Optional

class OfertaIn(BaseModel):
    titulo: str = Field(..., min_length=5, description="Título mínimo 5 caracteres")
    descripcion: str = Field(..., min_length=20, description="Descripción mínimo 20 caracteres")
    categoria: str = Field(..., description="Categoría (p.ej. 'Plomería', 'Electricidad', etc.)")
    ubicacion: str = Field(..., description="Ubicación del servicio")
    palabras_clave: List[str] = Field(..., min_items=1, description="Lista de palabras clave relevantes")
    costo: float = Field(..., gt=0, description="Costo del servicio, debe ser mayor que 0")
    horario: str = Field(..., description="Horario en que el proveedor está disponible")

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Reparación de tubería de cocina",
                "descripcion": "Necesito un plomero que repare una fuga en la tubería de la cocina...",
                "categoria": "Plomería",
                "ubicacion": "Bogotá, Colombia",
                "palabras_clave": ["fuga", "tubería", "cocina"],
                "costo": 50000.0,
                "horario": "Lun–Vie 15:00–18:00"
            }
        }
    }

class OfertaOut(BaseModel):
    id: str = Field(..., alias="_id")
    titulo: str
    descripcion: str
    categoria: str
    ubicacion: str
    palabras_clave: List[str]
    costo: float
    horario: str
    cliente_id: str
    cliente_nombre: str
    imagen_url: Optional[str] = None

    model_config = {"populate_by_name": True}

class OfertaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5)
    descripcion: Optional[str] = Field(None, min_length=20)
    categoria: Optional[str] = None
    ubicacion: Optional[str] = None
    palabras_clave: Optional[List[str]] = None
    costo: Optional[float] = Field(None, gt=0)
    horario: Optional[str] = None

    model_config = {"json_schema_extra": {"example": {}}}