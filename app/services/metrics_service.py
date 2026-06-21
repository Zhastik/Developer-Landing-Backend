from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsResponse


class MetricsService:
    def __init__(self) -> None:
        self.repository = MetricsRepository()

    def get_metrics(self) -> MetricsResponse:
        return MetricsResponse(**self.repository.get())
