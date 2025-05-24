from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.logging import logger, api_logger
from app.core.scheduler import task_scheduler
from app.api.v1.api import api_router
from app.core.database import SessionLocal
from app.core.config import settings
import traceback

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware pour logger les requêtes HTTP."""
    api_logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        api_logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        api_logger.error(f"Error details: {error_details}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Inclusion du router principal
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Endpoint racine qui retourne les informations de base de l'API."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Bienvenue sur l'API de gestion immobilière",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.on_event("startup")
async def startup_event():
    """Événement déclenché au démarrage de l'application."""
    logger.info("Application starting up...")
    
    # Initialiser le planificateur de tâches
    db = SessionLocal()
    try:
        task_scheduler.schedule_all_tasks(db)
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    """Événement déclenché à l'arrêt de l'application."""
    logger.info("Application shutting down...")
    
    # Arrêter le planificateur de tâches
    task_scheduler.shutdown()                           