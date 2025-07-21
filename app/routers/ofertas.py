# app/routers/oferta.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional
from bson import ObjectId
from app.db.db import db
from app.models.oferta import OfertaIn, OfertaOut, OfertaUpdate
from app.utils.images import save_image
from app.services.users_service import users_service  # 🔥 NUEVA IMPORTACIÓN
from datetime import datetime
import asyncio

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
        "created_at": datetime.utcnow(),   
        "visible": True,
    }
    # Subida de imagen (si existe)
    if imagen:
        url = save_image(imagen)  # tu helper de utils/images.py
        oferta_dict["imagen_url"] = url
    
    result = await db.ofertas.insert_one(oferta_dict)
    nuevo = await db.ofertas.find_one({"_id": result.inserted_id})
    nuevo["_id"] = str(nuevo["_id"])
    
    # 🔥 OBTENER INFO DEL USUARIO AL CREAR
    user_info = await users_service.get_user_info(cliente_id)
    if user_info:
        nuevo["cliente_foto_url"] = user_info.get("foto_url")
        nuevo["cliente_reputacion"] = user_info.get("reputacion", 0.0)
    
    return nuevo

@router.get("", response_model=List[OfertaOut])
async def listar_ofertas(
    skip: int = 0,
    limit: int = 1000,
    categoria: Optional[str] = Query(None),
    palabra_clave: Optional[str] = Query(None),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ubicación exacta"),
    costo_min: Optional[float] = Query(None, ge=0, description="Costo mínimo"),
    costo_max: Optional[float] = Query(None, ge=0, description="Costo máximo"),
    cliente_id: Optional[str] = Query(None, description="Filtrar por ID de cliente"),
    solo_visibles: bool = Query(True, description="True para filtrar solo ofertas visibles"),
):
    filtro = {}
    if solo_visibles:
        filtro["visible"] = True
        
    # Filtro por categoría
    if categoria:
        filtro["categoria"] = categoria
    # Filtro por palabra clave en título o descripción
    if palabra_clave:
        filtro["$or"] = [
            {"titulo": {"$regex": palabra_clave, "$options": "i"}},
            {"descripcion": {"$regex": palabra_clave, "$options": "i"}}
        ]
    # Filtro por ubicación
    if ubicacion:
        filtro["ubicacion"] = {"$regex": f"^{ubicacion}$", "$options": "i"}
    # Filtro por rango de costo
    if costo_min is not None or costo_max is not None:
        filtro["costo"] = {}
        if costo_min is not None:
            filtro["costo"]["$gte"] = costo_min
        if costo_max is not None:
            filtro["costo"]["$lte"] = costo_max
    if cliente_id:
        filtro["cliente_id"] = cliente_id

    cursor = db.ofertas.find(filtro).skip(skip).limit(limit)
    resultados = []
    
    # 🔥 OBTENER OFERTAS Y SUS USERS EN PARALELO
    ofertas_raw = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        ofertas_raw.append(doc)
    
    # Obtener información de todos los usuarios en paralelo
    if ofertas_raw:
        # Extraer IDs únicos de usuarios
        user_ids = list(set(oferta["cliente_id"] for oferta in ofertas_raw))
        
        # Crear tasks para obtener info de usuarios en paralelo
        user_tasks = [users_service.get_user_info(user_id) for user_id in user_ids]
        user_infos = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        # Crear un diccionario de user_id -> user_info
        user_info_dict = {}
        for user_id, user_info in zip(user_ids, user_infos):
            if isinstance(user_info, dict):  # No es excepción
                user_info_dict[user_id] = user_info
            else:
                user_info_dict[user_id] = None
        
        # Enriquecer cada oferta con la información del usuario
        for oferta in ofertas_raw:
            user_info = user_info_dict.get(oferta["cliente_id"])
            if user_info:
                oferta["cliente_foto_url"] = user_info.get("foto_url")
                oferta["cliente_reputacion"] = user_info.get("reputacion", 0.0)
            else:
                # Valores por defecto si no se pudo obtener la info
                oferta["cliente_foto_url"] = None
                oferta["cliente_reputacion"] = 0.0
            
            resultados.append(oferta)
    
    return resultados

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
    
    # 🔥 OBTENER INFO DEL USUARIO AL ACTUALIZAR
    user_info = await users_service.get_user_info(doc["cliente_id"])
    if user_info:
        doc["cliente_foto_url"] = user_info.get("foto_url")
        doc["cliente_reputacion"] = user_info.get("reputacion", 0.0)
    
    return doc

@router.patch("/{id}/visibility", response_model=OfertaOut)
async def cambiar_visibilidad(id: str, visible: bool = Form(..., description="Nuevo estado de visibilidad")):
    try:
        oid = ObjectId(id)
    except:
        raise HTTPException(400, "ID inválido")

    # Actualizamos solamente el campo `visible`
    result = await db.ofertas.update_one({"_id": oid}, {"$set": {"visible": visible}})
    if result.matched_count == 0:
        raise HTTPException(404, "Oferta no encontrada")

    # Devolvemos la oferta actualizada
    oferta = await db.ofertas.find_one({"_id": oid})
    oferta["_id"] = str(oferta["_id"])
    
    # 🔥 OBTENER INFO DEL USUARIO
    user_info = await users_service.get_user_info(oferta["cliente_id"])
    if user_info:
        oferta["cliente_foto_url"] = user_info.get("foto_url")
        oferta["cliente_reputacion"] = user_info.get("reputacion", 0.0)
    
    return oferta

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