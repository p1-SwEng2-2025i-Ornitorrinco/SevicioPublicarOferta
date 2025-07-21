# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.db import client
from app.routers import ofertas, categorias  # importa tus routers

app = FastAPI(title="Servicio: Publicar Oferta")

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Static files
app.mount("/images", StaticFiles(directory="images"), name="images")

# Routers
app.include_router(ofertas.router)
app.include_router(categorias.router)

@app.on_event("shutdown")
async def shutdown_db():
    client.close()
