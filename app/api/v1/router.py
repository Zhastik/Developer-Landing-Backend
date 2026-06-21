from fastapi import APIRouter

from app.api.v1.contact import router as contact_router
from app.api.v1.health import router as health_router
from app.api.v1.metrics import router as metrics_router

api_router = APIRouter(prefix="/api")
api_router.include_router(contact_router)
api_router.include_router(health_router)
api_router.include_router(metrics_router)
