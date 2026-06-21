from fastapi import APIRouter

from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    return MetricsService().get_metrics()
