from fastapi import FastAPI

from app.api.endpoints import router
from app.core.config import settings

app = FastAPI(
    title=f"API Banco {settings.BANCO_ID} - {settings.BANCO_NOMBRE}",
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Servicio API bancario activo",
        "banco_id": settings.BANCO_ID,
        "banco_nombre": settings.BANCO_NOMBRE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }