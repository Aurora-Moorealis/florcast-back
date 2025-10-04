# florcast-back

API backend desarrollada con FastAPI para el análisis y gestión de datos de plantas y flora.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para construir APIs
- **Estructura modular**: Organización clara con routers, models y services
- **Validación automática**: Validación de datos con Pydantic
- **Análisis de datos**: Integración con pandas y numpy para análisis estadístico
- **Funcionalidad geográfica**: Búsqueda de plantas por ubicación con geopy y shapely
- **Documentación interactiva**: Swagger UI y ReDoc incluidos
- **CORS habilitado**: Configuración lista para desarrollo frontend
- **Ejemplo CRUD completo**: Operaciones básicas implementadas para plantas

## 📚 Librerías Utilizadas

### Framework Web
- **FastAPI** (0.115.5) - Framework web moderno para construir APIs con Python
- **Uvicorn** (0.32.1) - Servidor ASGI de alto rendimiento
- **Pydantic** (2.10.3) - Validación de datos y configuración
- **Pydantic Settings** (2.6.1) - Gestión de configuración basada en variables de entorno
- **Python-dotenv** (1.0.1) - Carga de variables de entorno desde archivos .env

### Análisis de Datos
- **pandas** (2.2.3) - Manipulación y análisis de datos estructurados
- **numpy** (2.2.1) - Computación numérica y operaciones matemáticas avanzadas

### Geolocalización y Geografía
- **geopy** (2.4.1) - Cálculos de distancia geográfica y servicios de geocodificación
- **shapely** (2.0.6) - Manipulación y análisis de geometrías geoespaciales

Estas librerías permiten:
- ✅ Análisis estadístico avanzado de características de plantas
- ✅ Cálculo preciso de distancias entre ubicaciones geográficas
- ✅ Procesamiento y manipulación de datos geoespaciales
- ✅ Agregaciones, transformaciones y visualización de datos
- ✅ Validación robusta de coordenadas y datos geográficos

## 📁 Estructura del Proyecto

```
florcast-back/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuración de la aplicación
│   ├── models/                # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── plant.py           # Modelo de plantas
│   ├── routers/               # Endpoints de la API
│   │   ├── __init__.py
│   │   └── plants.py          # CRUD y búsquedas de plantas
│   └── services/              # Lógica de negocio
│       ├── __init__.py
│       └── plant_service.py   # Servicio de plantas con análisis
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

### Plantas CRUD

- `GET /api/v1/plants` - Obtener todas las plantas
- `GET /api/v1/plants/{plant_id}` - Obtener una planta específica
- `POST /api/v1/plants` - Crear una nueva planta
- `PUT /api/v1/plants/{plant_id}` - Actualizar una planta
- `DELETE /api/v1/plants/{plant_id}` - Eliminar una planta

### Análisis y Estadísticas

- `GET /api/v1/plants/statistics/summary` - Obtener estadísticas de las plantas (análisis con pandas/numpy)

### Búsqueda Geográfica

- `GET /api/v1/plants/search/nearby?latitude={lat}&longitude={lon}&radius_km={radius}` - Buscar plantas cerca de una ubicación

## 🌱 Modelo de Datos de Plantas

```json
{
  "scientific_name": "Rosa rubiginosa",
  "common_name": "Sweet Briar Rose",
  "family": "Rosaceae",
  "description": "Una especie de rosa silvestre con follaje fragante",
  "habitat": "Setos, matorrales y márgenes de bosques",
  "climate_zones": ["Templado", "Mediterráneo"],
  "latitude": 51.5074,
  "longitude": -0.1278,
  "location_name": "Londres, UK",
  "height_cm": 200.0,
  "bloom_season": "Primavera-Verano",
  "is_endangered": false
}
```

### Ejemplo de uso

**Crear una planta:**
```bash
curl -X POST "http://localhost:8000/api/v1/plants" \
  -H "Content-Type: application/json" \
  -d '{
    "scientific_name": "Quercus robur",
    "common_name": "Roble común",
    "family": "Fagaceae",
    "description": "Árbol caducifolio de gran tamaño",
    "habitat": "Bosques templados",
    "climate_zones": ["Templado"],
    "latitude": 40.4168,
    "longitude": -3.7038,
    "location_name": "Madrid, España",
    "height_cm": 4000.0,
    "bloom_season": "Primavera",
    "is_endangered": false
  }'
```

**Obtener todas las plantas:**
```bash
curl "http://localhost:8000/api/v1/plants"
```

**Obtener estadísticas:**
```bash
curl "http://localhost:8000/api/v1/plants/statistics/summary"
```

**Buscar plantas cercanas:**
```bash
curl "http://localhost:8000/api/v1/plants/search/nearby?latitude=40.4168&longitude=-3.7038&radius_km=500"
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