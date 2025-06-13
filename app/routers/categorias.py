from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from app.db.db import db
from app.models.categoria import CategoriaIn, CategoriaOut
from fastapi import UploadFile
from app.utils.images import save_image

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.post("", response_model=CategoriaOut, status_code=201)
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


@router.get("", response_model=List[CategoriaOut])
async def listar_categorias():
    cursor = db.categorias.find()
    lista = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        lista.append(doc)
    return lista


@router.delete("{categoria_id}", status_code=200)
async def eliminar_categoria(categoria_id: str):
    # Validar que el ID sea un ObjectId válido
    if not ObjectId.is_valid(categoria_id):
        raise HTTPException(status_code=400, detail="ID de categoría inválido")

    oid = ObjectId(categoria_id)
    result = await db.categorias.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return {"mensaje": "Categoría eliminada correctamente"}