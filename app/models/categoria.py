
from pydantic import BaseModel, Field
from typing import List, Optional

class CategoriaIn(BaseModel):
    nombre: str = Field(..., min_length=3, description="Nombre de la categoría, mínimo 3 caracteres")

    model_config = {
        "json_schema_extra": {
            "example": {"nombre": "Plomería"}
        }
    }

class CategoriaOut(BaseModel):
    id: str = Field(..., alias="_id")
    nombre: str

    model_config = {
        "populate_by_name": True
    }