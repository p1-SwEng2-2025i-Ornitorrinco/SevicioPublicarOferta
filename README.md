# Servicio Publicar Ofertas de Servicios

Este repositorio contiene un microservicio REST desarrollado con **FastAPI**, **Python** y **MongoDB** para gestionar la creación, consulta, actualización y eliminación de ofertas de servicios. Incluye filtros, paginación, CORS habilitado, subida de imágenes y una colección de categorías administrables.

---

## 📦 Tecnologías y dependencias

* **Python** 3.9+
* **FastAPI** para construir la API REST
* **Uvicorn** como servidor ASGI
* **Motor** (AsyncIO MongoDB driver) para acceso asíncrono a **MongoDB**
* **MongoDB** (local o Atlas)
* **Pydantic v2** para validación de datos
* **CORS Middleware** para permitir peticiones desde el frontend

Las dependencias están listadas en `requirements.txt`.

---

## 🚀 Instalación y arranque

1. Clona este repositorio:

   ```bash
   git clone https://github.com/tu-usuario/servicio-publicar-oferta.git
   cd servicio-publicar-oferta
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configura la conexión a MongoDB en `app/db.py` (por defecto `mongodb://localhost:27017`):

   ```python
   MONGO_URI = "mongodb://localhost:27017"
   ```

5. Arranca la aplicación en modo desarrollo:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   * La API se expondrá en `http://127.0.0.1:8000/`
   * Documentación interactiva en `http://127.0.0.1:8000/docs`

---

## 🗂 Estructura de carpetas

```
servicio-publicar-oferta/
├── app/
│   ├── main.py        # Definición de endpoints, modelos y configuración (CORS, estáticos)
│   └── db.py          # Conexión a MongoDB
├── images/            # Directorio para almacenar imágenes subidas
├── requirements.txt   # Dependencias del proyecto
└── README.md          # Documentación del proyecto
```

---

## 📑 Endpoints Principales

### Ofertas

| Método | Ruta            | Descripción                                             |
| ------ | --------------- | ------------------------------------------------------- |
| POST   | `/ofertas`      | Crear nueva oferta con datos y opcionalmente una imagen |
| GET    | `/ofertas`      | Listar ofertas (con filtros y paginación)               |
| GET    | `/ofertas/{id}` | Obtener detalle de una oferta                           |
| PUT    | `/ofertas/{id}` | Actualizar campos de una oferta y reemplazar imagen     |
| DELETE | `/ofertas/{id}` | Eliminar una oferta por ID                              |

#### POST /ofertas (multipart/form-data)

* **Campos (FormData)**:

  * `titulo` (string, min\_length=5)
  * `descripcion` (string, min\_length=20)
  * `categoria` (string)
  * `ubicacion` (string)
  * `palabras_clave` (string CSV, mínimo 1 palabra)
  * `costo` (float, > 0)
  * `horario` (string)
  * `imagen` (file, opcional)
* **Respuesta**: JSON de la oferta creada, incluyendo `imagen_url` si se subió imagen.

#### GET /ofertas

* **Query params**:

  * `skip` (int, default=0)
  * `limit` (int, default=10)
  * `categoria` (string, opcional)
  * `palabra_clave` (string, opcional)
* **Respuesta**: Array de ofertas.

#### GET /ofertas/{id}

* **Descripción**: Obtiene el detalle de una oferta por su ID.
* **Respuesta**: JSON de la oferta.

#### PUT /ofertas/{id} (multipart/form-data)

* **Campos (FormData)**: mismos que POST, todos opcionales.
* **Descripción**: Actualiza campos y permite reemplazar la imagen.

#### DELETE /ofertas/{id}

* **Descripción**: Elimina una oferta por su ID.
* **Respuesta**: Mensaje de confirmación.

### Categorías

| Método | Ruta                         | Descripción                 |
| ------ | ---------------------------- | --------------------------- |
| POST   | `/categorias`                | Crear nueva categoría       |
| GET    | `/categorias`                | Listar todas las categorías |
| DELETE | `/categorias/{categoria_id}` | Eliminar categoría por ID   |

---

## 🖼️ Servir Imágenes

* **Directorio local**: `images/`
* **Ruta montada**: `/images`
* **Acceso**: `http://localhost:8000/images/{nombre_de_archivo}`
* **Uso**: El campo `imagen_url` devuelve la URL relativa. Combínala con el host.

---

## 🔒 CORS

Se ha habilitado CORS con:

```python
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Ajusta `origins` en producción a tus dominios permitidos.

---

## 🚧 Buenas prácticas y próximos pasos

* Agregar autenticación (JWT) para proteger rutas sensibles.
* Validar existencia de la categoría al crear o actualizar ofertas.
* Añadir índices en MongoDB para mejorar rendimiento de filtros.
* Desplegar la API en un entorno productivo (Heroku, AWS, etc.)

---

