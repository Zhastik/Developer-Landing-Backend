from datetime import datetime
from uuid import uuid4
from typing import Optional

from app.repositories.contact_repository import ContactRepository
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.ai_service import AIService
from app.services.email_service import EmailService


class ContactService:
    def __init__(self) -> None:
        self.contact_repository = ContactRepository()
        self.metrics_repository = MetricsRepository()
        self.ai_service = AIService()
        self.email_service = EmailService()

    async def create_contact(self, payload: ContactCreate, request_id: Optional[str] = None) -> ContactResponse:
        generated_request_id = request_id or str(uuid4())

        ai_result = self.ai_service.analyze_contact(payload)
        email_result = await self.email_service.notify(payload, ai_result, generated_request_id)

        saved_contact = self.contact_repository.save(
            {
                "request_id": generated_request_id,
                "name": payload.name,
                "phone": payload.phone,
                "email": str(payload.email),
                "comment": payload.comment,
                "ai": ai_result.model_dump(),
                "email_delivery": email_result.model_dump(),
            }
        )
        self.metrics_repository.update_after_contact(saved_contact)

        return ContactResponse(
            status="accepted",
            request_id=generated_request_id,
            message="Обращение принято. Уведомления подготовлены к отправке.",
            created_at=datetime.fromisoformat(saved_contact["created_at"]),
            ai=ai_result,
            email=email_result,
        )
