from app.core.config import get_settings
from app.core.exceptions import RateLimitError
from app.repositories.rate_limit_repository import RateLimitRepository


class RateLimitService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository = RateLimitRepository()

    def check_contact_limit(self, client_key: str) -> None:
        is_allowed = self.repository.is_allowed(
            key=client_key,
            limit=self.settings.contact_rate_limit,
            window_seconds=self.settings.contact_rate_window_seconds,
        )
        if not is_allowed:
            raise RateLimitError()
