import json
import logging
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.schemas.contact import AIResult, ContactCreate

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def analyze_contact(self, payload: ContactCreate) -> AIResult:
        if not self.settings.ai_enabled or not self.settings.ai_api_key:
            return self._fallback(payload, error="AI disabled or AI_API_KEY is empty")

        try:
            try:
                from openai import OpenAI
            except ImportError as exc:
                return self._fallback(payload, error=f"openai package is not installed: {exc}")

            client_kwargs: Dict[str, Any] = {"api_key": self.settings.ai_api_key}
            base_url = self.settings.ai_base_url.strip()
            if base_url:
                client_kwargs["base_url"] = base_url

            client = OpenAI(**client_kwargs, timeout=self.settings.ai_timeout_seconds)

            completion = client.chat.completions.create(
                model=self.settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты backend AI-модуль для формы обратной связи на лендинге разработчика. "
                            "Верни только JSON без markdown. Поля: sentiment, category, auto_reply. "
                            "sentiment: positive | neutral | negative. "
                            "category: job_offer | project_request | consultation | complaint | spam | general. "
                            "auto_reply: короткий вежливый ответ пользователю на русском языке."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Имя: {payload.name}\n"
                            f"Email: {payload.email}\n"
                            f"Телефон: {payload.phone}\n"
                            f"Комментарий: {payload.comment}"
                        ),
                    },
                ],
                temperature=0.2,
            )

            raw_content = completion.choices[0].message.content or "{}"
            parsed = self._safe_json_loads(raw_content)

            return AIResult(
                available=True,
                sentiment=parsed.get("sentiment", "neutral"),
                category=parsed.get("category", "general"),
                auto_reply=parsed.get("auto_reply") or self._default_reply(payload.name),
                provider=self.settings.ai_provider,
                error=None,
            )
        except Exception as exc:  # noqa: BLE001 - fallback должен ловить любую ошибку провайдера
            logger.warning("AI provider unavailable: %s", exc)
            return self._fallback(payload, error=str(exc))

    def _safe_json_loads(self, raw_content: str) -> Dict[str, Any]:
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        try:
            result = json.loads(cleaned)
            return result if isinstance(result, dict) else {}
        except json.JSONDecodeError:
            logger.warning("AI returned non-json response: %s", raw_content[:300])
            return {}

    def _fallback(self, payload: ContactCreate, error: Optional[str] = None) -> AIResult:
        comment = payload.comment.lower()

        negative_words = ["плохо", "ошибка", "баг", "не работает", "срочно", "проблема"]
        positive_words = ["спасибо", "класс", "отлично", "интересно", "хочу", "понравилось"]
        spam_words = ["казино", "ставки", "кредит", "заработок", "crypto", "viagra"]

        if any(word in comment for word in spam_words):
            category = "spam"
        elif any(word in comment for word in ["проект", "сайт", "api", "backend", "разработка"]):
            category = "project_request"
        elif any(word in comment for word in ["вакансия", "работа", "офер", "резюме"]):
            category = "job_offer"
        elif any(word in comment for word in negative_words):
            category = "complaint"
        else:
            category = "general"

        if any(word in comment for word in negative_words):
            sentiment = "negative"
        elif any(word in comment for word in positive_words):
            sentiment = "positive"
        else:
            sentiment = "neutral"

        return AIResult(
            available=False,
            sentiment=sentiment,
            category=category,
            auto_reply=self._default_reply(payload.name),
            provider="fallback",
            error=error,
        )

    def _default_reply(self, name: str) -> str:
        return f"{name}, спасибо за обращение! Я получил ваше сообщение и скоро свяжусь с вами."
