# florcast-back

API backend desarrollada con FastAPI para el proyecto florcast.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para construir APIs
- **Estructura modular**: Organización clara con routers, models y services
- **Validación automática**: Validación de datos con Pydantic
- **Documentación interactiva**: Swagger UI y ReDoc incluidos
- **CORS habilitado**: Configuración lista para desarrollo frontend
- **Ejemplo CRUD completo**: Operaciones básicas implementadas

## 📁 Estructura del Proyecto

```
florcast-back/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuración de la aplicación
│   ├── models/                # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── item.py
│   ├── routers/               # Endpoints de la API
│   │   ├── __init__.py
│   │   └── items.py
│   └── services/              # Lógica de negocio
│       ├── __init__.py
│       └── item_service.py
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias del proyecto
├── .env.example              # Variables de entorno de ejemplo
└── README.md
```

## 🛠️ Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Aurora-Moorealis/florcast-back.git
cd florcast-back
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🚀 Uso

### Ejecutar el servidor de desarrollo

```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Endpoints principales

- `GET /` - Página de bienvenida
- `GET /health` - Estado de salud de la API

### Items CRUD

- `GET /api/v1/items` - Obtener todos los items
- `GET /api/v1/items/{item_id}` - Obtener un item específico
- `POST /api/v1/items` - Crear un nuevo item
- `PUT /api/v1/items/{item_id}` - Actualizar un item
- `DELETE /api/v1/items/{item_id}` - Eliminar un item

### Ejemplo de uso

**Crear un item:**
```bash
curl -X POST "http://localhost:8000/api/v1/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nuevo Item",
    "description": "Descripción del item",
    "price": 49.99,
    "is_available": true
  }'
```

**Obtener todos los items:**
```bash
curl "http://localhost:8000/api/v1/items"
```

## 🔧 Configuración

Las variables de entorno se configuran en el archivo `.env`:

```env
# Application Configuration
APP_NAME=florcast-back
APP_VERSION=1.0.0
DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 🏗️ Extender la API

### Agregar un nuevo endpoint

1. **Crear el modelo** en `app/models/`:
```python
from pydantic import BaseModel

class MyModel(BaseModel):
    field1: str
    field2: int
```

2. **Crear el servicio** en `app/services/`:
```python
class MyService:
    def get_data(self):
        return {"data": "example"}
```

3. **Crear el router** en `app/routers/`:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

4. **Registrar el router** en `main.py`:
```python
from app.routers import my_router

app.include_router(my_router.router, prefix="/api/v1", tags=["my-tag"])
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias o mejoras.