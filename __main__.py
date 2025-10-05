from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import plants
import app

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API of floration events"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(plants.router, prefix="/api/v1", tags=["plants"])

@app.get("/")
async def root():
    """Root endpoint"""
    
    return {
        "message": "Welcome to florcast-back API - API of flowers",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "description": app.description # type: ignore
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "__main__:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
