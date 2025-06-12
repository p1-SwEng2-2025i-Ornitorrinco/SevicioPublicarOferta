# app/main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from app.db import db, client


app = FastAPI(title="Servicio: Publicar Oferta")

# Opcional: cerrar Mongo al apagar FastAPI
@app.on_event("shutdown")
async def close_mongo():
    client.close()

# Configurar CORS
origins = ["*"]  # Cambiar a lista de dominios específicos en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos Pydantic para Pydantic ---

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

    model_config = {
        "populate_by_name": True
    }

class OfertaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, description="Título mínimo 5 caracteres")
    descripcion: Optional[str] = Field(None, min_length=20, description="Descripción mínimo 20 caracteres")
    categoria: Optional[str] = Field(None, description="Categoría (p.ej. 'Plomería', 'Electricidad', etc.)")
    ubicacion: Optional[str] = Field(None, description="Ubicación del servicio")
    palabras_clave: Optional[List[str]] = Field(None, min_items=1, description="Lista de palabras clave relevantes")
    costo: Optional[float] = Field(None, gt=0, description="Costo del servicio, debe ser mayor que 0")
    horario: Optional[str] = Field(None, description="Horario en que el proveedor está disponible")

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Clases de guitarra avanzado",
                "descripcion": "Clases avanzadas de guitarra: acordes, escalas y técnica...",
                "categoria": "Música",
                "ubicacion": "Medellín, Colombia",
                "palabras_clave": ["guitarra", "música", "avanzado"],
                "costo": 80000.0,
                "horario": "Lun–Vie 16:00–20:00"
            }
        }
    }

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

# ─── Endpoints básicos ─────────────────────────────────────────────────────────

@app.get("/")
async def read_root():
    return {"mensaje": "API de Publicar Oferta funcionando"}

@app.get("/status")
async def status():
    return {"status": "OK"}

# ─── CRUD de Ofertas ───────────────────────────────────────────────────────────

@app.post("/ofertas", response_model=OfertaOut, status_code=201)
async def crear_oferta(oferta: OfertaIn):
    oferta_dict = oferta.model_dump()
    result = await db.ofertas.insert_one(oferta_dict)
    nuevo_doc = await db.ofertas.find_one({"_id": result.inserted_id})
    if not nuevo_doc:
        raise HTTPException(status_code=500, detail="Error al crear oferta")
    nuevo_doc["_id"] = str(nuevo_doc["_id"])
    return nuevo_doc

@app.get("/ofertas", response_model=List[OfertaOut])
async def listar_ofertas(
    skip: int = 0,
    limit: int = 10,
    categoria: Optional[str] = Query(None),
    palabra_clave: Optional[str] = Query(None),
):
    filtro = {}
    if categoria:
        filtro["categoria"] = categoria
    if palabra_clave:
        filtro["$or"] = [
            {"titulo": {"$regex": palabra_clave, "$options": "i"}},
            {"descripcion": {"$regex": palabra_clave, "$options": "i"}}
        ]
    cursor = db.ofertas.find(filtro).skip(skip).limit(limit)
    ofertas = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        ofertas.append(doc)
    return ofertas

@app.get("/ofertas/{id}", response_model=OfertaOut)
async def obtener_oferta(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    oferta = await db.ofertas.find_one({"_id": obj_id})
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    oferta["_id"] = str(oferta["_id"])
    return oferta

@app.put("/ofertas/{id}", response_model=OfertaOut)
async def actualizar_oferta(id: str, datos: OfertaUpdate):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    existe = await db.ofertas.find_one({"_id": obj_id})
    if not existe:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    update_data = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    if "categoria" in update_data:
        cat = await db.categorias.find_one({"nombre": update_data["categoria"]})
        if not cat:
            raise HTTPException(status_code=400, detail="La categoría especificada no existe")
    await db.ofertas.update_one({"_id": obj_id}, {"$set": update_data})
    doc_actualizado = await db.ofertas.find_one({"_id": obj_id})
    doc_actualizado["_id"] = str(doc_actualizado["_id"])
    return doc_actualizado

@app.delete("/ofertas/{id}", status_code=200)
async def eliminar_oferta(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    result = await db.ofertas.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"mensaje": "Oferta eliminada correctamente"}


# --- MODELOS PARA CATEGORÍAS ---

class CategoriaIn(BaseModel):
    nombre: str = Field(..., min_length=3, description="Nombre de la categoría, mínimo 3 caracteres")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Plomería"
            }
        }
    }


class CategoriaOut(BaseModel):
    id: str = Field(..., alias="_id")
    nombre: str

    model_config = {
        "populate_by_name": True
    }


# --- RUTAS PARA CATEGORÍAS ---

@app.post("/categorias", response_model=CategoriaOut, status_code=201)
async def crear_categoria(cat: CategoriaIn):
    # 1. Insertar la categoría en Mongo
    cat_dict = cat.model_dump()
    result = await db.categorias.insert_one(cat_dict)

    # 2. Recuperar el documento recién creado
    nuevo_doc = await db.categorias.find_one({"_id": result.inserted_id})
    if not nuevo_doc:
        raise HTTPException(status_code=500, detail="Error al crear categoría")

    # 3. Convertir ObjectId a str
    nuevo_doc["_id"] = str(nuevo_doc["_id"])
    return nuevo_doc


@app.get("/categorias", response_model=List[CategoriaOut])
async def listar_categorias():
    cursor = db.categorias.find()
    lista = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        lista.append(doc)
    return lista


@app.delete("/categorias/{categoria_id}", status_code=200)
async def eliminar_categoria(categoria_id: str):
    # Validar que el ID sea un ObjectId válido
    if not ObjectId.is_valid(categoria_id):
        raise HTTPException(status_code=400, detail="ID de categoría inválido")

    oid = ObjectId(categoria_id)
    result = await db.categorias.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return {"mensaje": "Categoría eliminada correctamente"}