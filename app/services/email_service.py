import logging
import smtplib
from email.message import EmailMessage
from typing import Dict, List, Optional

from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.schemas.contact import AIResult, ContactCreate, EmailResult
from app.utils.json_file import JsonFileStorage

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.outbox = JsonFileStorage(self.settings.data_path / "outbox.jsonl")

    async def notify(self, payload: ContactCreate, ai_result: AIResult, request_id: str) -> EmailResult:
        owner_email = self._build_owner_email(payload, ai_result, request_id)
        user_email = self._build_user_email(payload, ai_result, request_id)

        if not self.settings.mail_enabled:
            self._save_to_outbox([owner_email, user_email], request_id)
            return EmailResult(owner_sent=True, user_copy_sent=True, mode="file_outbox")

        try:
            await run_in_threadpool(self._send_many, [owner_email, user_email])
            return EmailResult(owner_sent=True, user_copy_sent=True, mode="smtp")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Email delivery failed request_id=%s", request_id)
            self._save_to_outbox([owner_email, user_email], request_id, error=str(exc))
            return EmailResult(owner_sent=False, user_copy_sent=False, mode="file_outbox", error=str(exc))

    def _send_many(self, messages: List[EmailMessage]) -> None:
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as smtp:
            smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            for message in messages:
                smtp.send_message(message)

    def _build_owner_email(self, payload: ContactCreate, ai_result: AIResult, request_id: str) -> EmailMessage:
        body = f"""
Новое обращение с лендинга.

Request ID: {request_id}
Имя: {payload.name}
Телефон: {payload.phone}
Email: {payload.email}

Комментарий:
{payload.comment}

AI-анализ:
- Доступен: {ai_result.available}
- Провайдер: {ai_result.provider}
- Тональность: {ai_result.sentiment}
- Категория: {ai_result.category}
- Автоответ: {ai_result.auto_reply}
- Ошибка AI: {ai_result.error or "нет"}
""".strip()
        return self._message(
            to_email=self.settings.site_owner_email,
            subject=f"Новое обращение с лендинга: {payload.name}",
            body=body,
        )

    def _build_user_email(self, payload: ContactCreate, ai_result: AIResult, request_id: str) -> EmailMessage:
        body = f"""
Здравствуйте, {payload.name}!

{ai_result.auto_reply}

Номер вашего обращения: {request_id}

С уважением,
Команда сайта.
""".strip()
        return self._message(
            to_email=str(payload.email),
            subject="Мы получили ваше обращение",
            body=body,
        )

    def _message(self, to_email: str, subject: str, body: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.settings.smtp_from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        return message

    def _save_to_outbox(self, messages: List[EmailMessage], request_id: str, error: Optional[str] = None) -> None:
        for message in messages:
            self.outbox.append_jsonl(
                {
                    "request_id": request_id,
                    "to": message["To"],
                    "subject": message["Subject"],
                    "body": message.get_content(),
                    "error": error,
                }
            )
