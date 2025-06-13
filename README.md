# README.md

## Proyecto: Servicio de Publicación de Ofertas

Este repositorio contiene un microservicio REST en **FastAPI** para gestionar ofertas de servicios.

### Tecnologías

* **Python 3.9+**
* **FastAPI**
* **MongoDB** (vía Motor)
* **Uvicorn** (servidor ASGI)
* **CORS Middleware**
* **Subida de imágenes** (almacenamiento local)

### Requisitos Previos

1. Python 3.9+ instalado.
2. MongoDB corriendo localmente o en Atlas (URI en `app/db.py`).
3. `git` y cuenta de GitHub.

### Instalación y Ejecución

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/servicio-publicar-oferta.git
cd servicio-publicar-oferta

# Crear y activar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear carpeta para imágenes (si no existe)
mkdir images

# Ejecutar servidor en modo desarrollo
uvicorn app.main:app --reload --port 8001
```

### Documentación de Endpoints

La API expone documentación Swagger automática en:

```
http://127.0.0.1:8001/docs
```

Allí es posible ver y probar todos los endpoints:

* `POST   /ofertas`        : Crear oferta (multipart/form-data, incluye imagen y datos de cliente).

* `GET    /ofertas`        : Listar ofertas con filtros (`skip`, `limit`, `categoria`, `palabra_clave`).

* `GET    /ofertas/{id}`   : Obtener detalle de una oferta.

* `PUT    /ofertas/{id}`   : Actualizar oferta (permite campos parciales y nueva imagen).

* `DELETE /ofertas/{id}`   : Eliminar oferta.

* `POST   /categorias`     : Crear categoría.

* `GET    /categorias`     : Listar categorías.

* `DELETE /categorias/{id}`: Eliminar categoría.

### Servir Imágenes

Las imágenes subidas se almacenan en la carpeta `images/` y se sirven estáticamente:

```
http://127.0.0.1:8000/images/{nombre_de_archivo}
```

---

# CHANGELOG.md

## \[1.0.0] - 2025-06-13

### Agregado

* CRUD completo de ofertas con campos: título, descripción, categoría, ubicación, palabras clave, costo, horario, cliente\_id, cliente\_nombre.
* Soporte de subida de imágenes en creación y edición de ofertas.
* Endpoints de categorías (crear, listar, eliminar).
* Filtros y paginación en `GET /ofertas`.
* CORS habilitado y configuración de carpeta estática para imágenes.

### Cambios

* Eliminado campo de reputación en ofertas.

### Documentación

* Swagger UI disponible en `/docs`.

*Fin del documento*
