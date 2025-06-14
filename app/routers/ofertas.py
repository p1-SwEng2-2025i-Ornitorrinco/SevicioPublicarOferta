from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional
from bson import ObjectId
from app.db.db import db
from app.models.oferta import OfertaIn, OfertaOut, OfertaUpdate
from app.utils.images import save_image
from datetime import datetime


router = APIRouter(prefix="/ofertas", tags=["Ofertas"])

@router.post("", response_model=OfertaOut, status_code=201)
async def crear_oferta(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...),
    ubicacion: str = Form(...),
    palabras_clave: Optional[str] = Form(None),  # CSV opcional
    costo: float = Form(...),
    horario: Optional[str] = Form(None),
    cliente_id: str = Form(...),
    cliente_nombre: str = Form(...),
    imagen: Optional[UploadFile] = File(None),
):
    # Procesar palabras clave si vienen
    claves = [kw.strip() for kw in (palabras_clave or "").split(",") if kw.strip()] or None

    oferta_dict = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "ubicacion": ubicacion,
        "palabras_clave": claves,
        "costo": costo,
        "horario": horario,
        "cliente_id": cliente_id,
        "cliente_nombre": cliente_nombre,
        "created_at": datetime.utcnow(),   # ← fecha de creación
    }

    # Subida de imagen (si existe)
    if imagen:
        url = save_image(imagen)  # tu helper de utils/images.py
        oferta_dict["imagen_url"] = url

    result = await db.ofertas.insert_one(oferta_dict)
    nuevo = await db.ofertas.find_one({"_id": result.inserted_id})
    nuevo["_id"] = str(nuevo["_id"])
    return nuevo

@router.get("", response_model=List[OfertaOut])
async def listar_ofertas(
    skip: int = 0,
    limit: int = 100,
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

@router.put("", response_model=OfertaOut)
async def actualizar_oferta(
    id: str,
    datos: OfertaUpdate,
    imagen: Optional[UploadFile] = File(None),
):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    existe = await db.ofertas.find_one({"_id": obj_id})
    if not existe:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    update_data = {k: v for k, v in datos.model_dump().items() if v is not None}
    # Procesar nueva imagen
    if imagen:
        ext = os.path.splitext(imagen.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join("images", filename)
        with open(file_path, "wb") as f:
            content = await imagen.read()
            f.write(content)
        update_data["imagen_url"] = f"/images/{filename}"

    await db.ofertas.update_one({"_id": obj_id}, {"$set": update_data})
    doc = await db.ofertas.find_one({"_id": obj_id})
    doc["_id"] = str(doc["_id"])
    return doc

@router.delete("", status_code=200)
async def eliminar_oferta(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    result = await db.ofertas.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"mensaje": "Oferta eliminada correctamente"}
