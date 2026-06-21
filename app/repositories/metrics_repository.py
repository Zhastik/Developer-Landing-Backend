from collections import Counter
from typing import Any, Dict

from app.core.config import get_settings
from app.utils.json_file import JsonFileStorage


class MetricsRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self.storage = JsonFileStorage(settings.data_path / "metrics.json")

    def get_default(self) -> Dict[str, Any]:
        return {
            "total_contacts": 0,
            "ai_success": 0,
            "ai_failures": 0,
            "email_success": 0,
            "email_failures": 0,
            "by_category": {},
            "by_sentiment": {},
            "last_contact_at": None,
        }

    def get(self) -> Dict[str, Any]:
        return self.storage.read_json(default=self.get_default())

    def update_after_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        metrics = self.get()
        metrics["total_contacts"] = int(metrics.get("total_contacts", 0)) + 1

        ai = contact.get("ai", {})
        email = contact.get("email_delivery", {})

        if ai.get("available"):
            metrics["ai_success"] = int(metrics.get("ai_success", 0)) + 1
        else:
            metrics["ai_failures"] = int(metrics.get("ai_failures", 0)) + 1

        if email.get("owner_sent") and email.get("user_copy_sent"):
            metrics["email_success"] = int(metrics.get("email_success", 0)) + 1
        else:
            metrics["email_failures"] = int(metrics.get("email_failures", 0)) + 1

        category_counter = Counter(metrics.get("by_category", {}))
        sentiment_counter = Counter(metrics.get("by_sentiment", {}))
        category_counter[ai.get("category", "unknown")] += 1
        sentiment_counter[ai.get("sentiment", "unknown")] += 1

        metrics["by_category"] = dict(category_counter)
        metrics["by_sentiment"] = dict(sentiment_counter)
        metrics["last_contact_at"] = contact.get("created_at")

        self.storage.write_json(metrics)
        return metrics
