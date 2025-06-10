# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from app.db import db, client

app = FastAPI(title="Servicio: Publicar Oferta")

# Opcional: cerrar Mongo al apagar FastAPI
@app.on_event("shutdown")
async def close_mongo():
    client.close()


# --- Modelos Pydantic para Pydantic v2 ---

class OfertaIn(BaseModel):
    titulo: str = Field(..., min_length=5, description="Título mínimo 5 caracteres")
    descripcion: str = Field(..., min_length=20, description="Descripción mínimo 20 caracteres")
    categoria: str = Field(..., description="Categoría (p.ej. 'Plomería', 'Electricidad', etc.)")
    horario: str = Field(..., description="Horario en que el proveedor está disponible")

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Reparación de tubería de cocina",
                "descripcion": "Soy un plomero que repara una fugas en la tubería de la cocina, preferiblemente entre semana de 3pm a 6pm.",
                "categoria": "Plomería",
                "horario": "Lun–Vie 15:00–18:00"
            }
        }
    }


class OfertaOut(BaseModel):
    id: str = Field(..., alias="_id")
    titulo: str
    descripcion: str
    categoria: str
    horario: str
    reputacion: float

    model_config = {
        "populate_by_name": True
    }

# Modelo de actualizacion de actualizar oferta

from typing import Optional

class OfertaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, description="Título mínimo 5 caracteres")
    descripcion: Optional[str] = Field(None, min_length=20, description="Descripción mínimo 20 caracteres")
    categoria: Optional[str] = Field(None, description="Categoría (p.ej. 'Plomería', 'Electricidad', etc.)")
    horario: Optional[str] = Field(None, description="Horario en que el proveedor está disponible")

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Clases de guitarra (avanzado)",
                "descripcion": "Doy clases particulares avanzadas de guitarra: acordes complejos, escalas y técnica. Zona norte, 2 horas por sesión.",
                "categoria": "Música",
                "horario": "Lun–Viernes 16:00–20:00"
            }
        }
    }


# --- Endpoints de prueba ---

@app.get("/")
async def read_root():
    return {"mensaje": "API de Publicar Oferta funcionando"}


@app.get("/status")
async def status():
    return {"status": "OK"}


# --- Crear nueva oferta ---
@app.post("/ofertas", response_model=OfertaOut, status_code=201)
async def crear_oferta(oferta: OfertaIn):
    oferta_dict = oferta.model_dump()  # Diccionario limpio validado por Pydantic
    oferta_dict["reputacion"] = 0.0

    # Aquí, db.ofertas nunca será None porque lo inicializamos en db.py
    result = await db.ofertas.insert_one(oferta_dict)

    # Dentro de crear_oferta:
    existe = await db.categorias.find_one({"nombre": oferta_dict["categoria"]})
    if not existe:
        raise HTTPException(status_code=400, detail="Categoría no existe")
    
    # Recuperamos el documento recién insertado
    nuevo_doc = await db.ofertas.find_one({"_id": result.inserted_id})
    if not nuevo_doc:
        raise HTTPException(status_code=500, detail="Error al crear oferta")

    # Convertimos ObjectId a str para que Pydantic lo serialice bien
    nuevo_doc["_id"] = str(nuevo_doc["_id"])
    return nuevo_doc


# --- Listar todas las ofertas con o sin filtro ---
from fastapi import Query

@app.get("/ofertas", response_model=List[OfertaOut])
async def listar_ofertas(
    id: Optional[str] = Query(None, description="ID de la oferta"),
    skip: int = 0,
    limit: int = 10,
    categoria: str | None = Query(default=None),
    palabra_clave: str | None = Query(default=None),
):
    # Construir el filtro dinámicamente
    filtro = {}
    if id:
        try:
            filtro["_id"] = ObjectId(id)
        except:
            raise HTTPException(status_code=400, detail="ID inválido")
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

#PUT ofertas

@app.put("/ofertas/{id}", response_model=OfertaOut)
async def actualizar_oferta(id: str, datos: OfertaUpdate):
    # 1. Convertir y validar el ID
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")

    # 2. Verificar que exista la oferta
    existe = await db.ofertas.find_one({"_id": obj_id})
    if not existe:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    # 3. Construir dict con solo los campos presentes en el body
    update_data = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    # 4. (Opcional) Validar que la categoría nueva exista
    if "categoria" in update_data:
        cat = await db.categorias.find_one({"nombre": update_data["categoria"]})
        if not cat:
            raise HTTPException(status_code=400, detail="La categoría especificada no existe")

    # 5. Ejecutar el update en MongoDB
    await db.ofertas.update_one({"_id": obj_id}, {"$set": update_data})

    # 6. Recuperar el documento actualizado
    doc_actualizado = await db.ofertas.find_one({"_id": obj_id})
    doc_actualizado["_id"] = str(doc_actualizado["_id"])
    return doc_actualizado

# DELETE Ofertas

@app.delete("/ofertas/{id}", status_code=200)
async def eliminar_oferta(id: str):
    # 1. Validar formato de ID
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")

    # 2. Intentar eliminar
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