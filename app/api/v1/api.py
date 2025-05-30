from fastapi import APIRouter

from app.api.v1.endpoints import auth, properties, contracts, payments, maintenance

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"]) 