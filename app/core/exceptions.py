class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


class RateLimitError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=429,
            code="rate_limit_exceeded",
            message="Слишком много обращений. Попробуйте позже.",
        )


class EmailDeliveryError(AppError):
    def __init__(self, message: str = "Не удалось отправить email") -> None:
        super().__init__(status_code=502, code="email_delivery_failed", message=message)
