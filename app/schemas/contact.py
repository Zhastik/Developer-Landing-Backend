from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, examples=["Жаслан"])
    phone: str = Field(..., min_length=5, max_length=30, examples=["+7 999 123-45-67"])
    email: EmailStr = Field(..., examples=["client@example.com"])
    comment: str = Field(..., min_length=10, max_length=2000, examples=["Здравствуйте, хочу обсудить разработку backend API."])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Имя не может быть пустым")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.strip()
        allowed = set("0123456789+()- ")
        if any(char not in allowed for char in cleaned):
            raise ValueError("Телефон содержит недопустимые символы")
        digits_count = sum(char.isdigit() for char in cleaned)
        if digits_count < 5:
            raise ValueError("Телефон должен содержать минимум 5 цифр")
        return cleaned

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Комментарий слишком короткий")
        return cleaned


class AIResult(BaseModel):
    available: bool
    sentiment: Literal["positive", "neutral", "negative", "unknown"]
    category: str
    auto_reply: str
    provider: str
    error: Optional[str] = None


class EmailResult(BaseModel):
    owner_sent: bool
    user_copy_sent: bool
    mode: Literal["smtp", "file_outbox"]
    error: Optional[str] = None


class ContactResponse(BaseModel):
    status: Literal["accepted"]
    request_id: str
    message: str
    created_at: datetime
    ai: AIResult
    email: EmailResult
